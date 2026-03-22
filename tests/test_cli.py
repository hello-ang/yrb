import unittest
from click.testing import CliRunner
from yrb.cli.cli import cli
from yrb.core.config_manager import load_config, set_config_value, unset_config_value

class TestCli(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_help(self):
        """测试帮助命令"""
        result = self.runner.invoke(cli, ['--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Python国内下载加速工具', result.output)

    def test_config_lifecycle(self):
        """测试配置的增删改查"""
        # 1. Set
        result = self.runner.invoke(cli, ['config', 'set', 'test.key', 'test_value'])
        self.assertEqual(result.exit_code, 0)
        # Rich 输出包含: ✓ 已设置 test.key = test_value
        self.assertIn('test.key', result.output)
        self.assertIn('test_value', result.output)
        
        # Verify persistence
        config = load_config()
        self.assertEqual(config.get('test', {}).get('key'), 'test_value')

        # 2. Get
        result = self.runner.invoke(cli, ['config', 'get', 'test.key'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('test.key', result.output)
        self.assertIn('test_value', result.output)

        # 3. Unset
        result = self.runner.invoke(cli, ['config', 'unset', 'test.key'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('test.key', result.output)
        
        # Verify removal
        config = load_config()
        self.assertIsNone(config.get('test', {}).get('key'))

    def test_info(self):
        """测试 info 命令"""
        result = self.runner.invoke(cli, ['info'])
        self.assertEqual(result.exit_code, 0)
        # Rich 输出包含镜像源表格标题或降级时的纯文本
        self.assertTrue(
            '镜像源' in result.output or 'Supported Mirrors:' in result.output,
            f"Expected mirror info in output, got: {result.output[:200]}"
        )

if __name__ == '__main__':
    unittest.main()
