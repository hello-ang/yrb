import unittest
import shutil
import tempfile
import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from yrb.core import config_manager
from yrb.core import cache_manager
from yrb.core import speed_test

class TestCore(unittest.TestCase):
    def setUp(self):
        # 创建临时目录用于测试配置和缓存
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        
        # Mock 路径配置
        self.config_patcher = patch('yrb.core.config_manager.CONFIG_DIR', self.test_path)
        self.config_file_patcher = patch('yrb.core.config_manager.CONFIG_FILE', self.test_path / "config.json")
        self.cache_dir_patcher = patch('yrb.core.cache_manager.CACHE_DIR', self.test_path / "cache")
        self.cache_index_patcher = patch('yrb.core.cache_manager.CACHE_INDEX_FILE', self.test_path / "cache" / "index.json")
        self.speed_cache_patcher = patch('yrb.core.speed_test.SPEED_CACHE_FILE', self.test_path / "cache" / "speed_cache.json")
        
        self.config_patcher.start()
        self.config_file_patcher.start()
        self.cache_dir_patcher.start()
        self.cache_index_patcher.start()
        self.speed_cache_patcher.start()

    def tearDown(self):
        self.config_patcher.stop()
        self.config_file_patcher.stop()
        self.cache_dir_patcher.stop()
        self.cache_index_patcher.stop()
        self.speed_cache_patcher.stop()
        shutil.rmtree(self.test_dir)

    def test_config_manager(self):
        """测试配置管理模块"""
        # 测试设置嵌套键
        config_manager.set_config_value("pip.mirror", "aliyun")
        self.assertEqual(config_manager.get_config_value("pip.mirror"), "aliyun")
        
        # 测试读取完整配置
        config = config_manager.load_config()
        self.assertEqual(config["pip"]["mirror"], "aliyun")
        
        # 测试删除键
        config_manager.unset_config_value("pip.mirror")
        self.assertIsNone(config_manager.get_config_value("pip.mirror"))
        
        # 测试 Section 自动清理
        config = config_manager.load_config()
        self.assertNotIn("pip", config)

    def test_cache_manager(self):
        """测试缓存管理模块"""
        # 准备测试文件
        src_file = self.test_path / "test.whl"
        with open(src_file, "w") as f:
            f.write("dummy content")
            
        # 测试写入缓存
        success = cache_manager.cache_package("numpy", "1.0.0", str(src_file))
        self.assertTrue(success)
        
        # 测试读取缓存
        cached_path = cache_manager.get_cached_package("numpy", "1.0.0")
        self.assertTrue(os.path.exists(cached_path))
        self.assertEqual(Path(cached_path).name, "test.whl")
        
        # 测试清理缓存
        cache_manager.clean_cache()
        self.assertFalse(os.path.exists(cached_path))

    @patch('requests.head')
    def test_speed_test(self, mock_head):
        """测试测速模块"""
        # Mock 网络响应
        mock_resp_fast = MagicMock()
        mock_resp_fast.status_code = 200
        
        mock_resp_slow = MagicMock()
        mock_resp_slow.status_code = 200
        
        # 模拟不同延迟：通过 side_effect 控制 requests.head 的耗时
        # 注意：speed_test 使用 time.time() 计算耗时，这里主要验证逻辑流程
        # 简单起见，我们只 Mock status_code，逻辑层会认为都很快
        mock_head.return_value = mock_resp_fast
        
        mirrors = [
            {"name": "fast", "url": "http://fast.com"},
            {"name": "slow", "url": "http://slow.com"}
        ]
        
        # 强制测速
        best = speed_test.get_best_mirror(mirrors, force=True)
        self.assertIn(best["name"], ["fast", "slow"])
        self.assertIn("delay", best)

    def test_speed_test_lock(self):
        """测试测速模块的配置锁定功能"""
        # 锁定镜像
        config_manager.set_config_value("pip.mirror", "locked_mirror")
        
        mirrors = [
            {"name": "other", "url": "http://other.com"},
            {"name": "locked_mirror", "url": "http://locked.com"}
        ]
        
        # 传入 tool_name='pip'，应直接返回锁定镜像，不进行网络请求
        with patch('requests.head') as mock_head:
            best = speed_test.get_best_mirror(mirrors, tool_name="pip")
            self.assertEqual(best["name"], "locked_mirror")
            mock_head.assert_not_called()

if __name__ == '__main__':
    unittest.main()
