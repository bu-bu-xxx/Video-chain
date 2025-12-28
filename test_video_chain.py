"""
Unit tests for Video Chain Workflow

These tests validate the core functionality without requiring API keys.
They use mocking to simulate API responses.
"""
import unittest
from unittest.mock import Mock, patch, MagicMock, mock_open
import os
import sys
import tempfile
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from video_chain import VideoChainWorkflow


class TestVideoChainWorkflow(unittest.TestCase):
    """Test cases for VideoChainWorkflow class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_api_key = "sk-test-key-123"
        os.environ['AIHUBMIX_API_KEY'] = self.test_api_key
        
    def tearDown(self):
        """Clean up after tests"""
        if 'AIHUBMIX_API_KEY' in os.environ:
            del os.environ['AIHUBMIX_API_KEY']
    
    def test_initialization_with_api_key(self):
        """Test workflow initialization with API key"""
        workflow = VideoChainWorkflow(api_key=self.test_api_key)
        self.assertEqual(workflow.api_key, self.test_api_key)
        self.assertEqual(workflow.base_url, "https://aihubmix.com/v1")
        
    def test_initialization_without_api_key_raises_error(self):
        """Test that initialization without API key raises ValueError"""
        del os.environ['AIHUBMIX_API_KEY']
        with self.assertRaises(ValueError) as context:
            VideoChainWorkflow()
        self.assertIn("API key is required", str(context.exception))
    
    @patch('video_chain.OpenAI')
    def test_generate_prompts_basic(self, mock_openai):
        """Test basic prompt generation"""
        # Mock the API response
        mock_response = Mock()
        mock_response.output = [Mock(content='{"segments": ["片段1", "片段2", "片段3"]}')]
        mock_client = Mock()
        mock_client.responses.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        workflow = VideoChainWorkflow(api_key=self.test_api_key)
        prompts = workflow.generate_prompts("测试描述", num_segments=3)
        
        self.assertEqual(len(prompts), 3)
        self.assertEqual(prompts[0], "片段1")
        
    @patch('video_chain.OpenAI')
    def test_generate_prompts_fallback(self, mock_openai):
        """Test prompt generation with fallback on invalid JSON"""
        # Mock the API response with invalid JSON
        mock_response = Mock()
        mock_response.output = [Mock(content='片段1\n片段2\n片段3')]
        mock_client = Mock()
        mock_client.responses.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        workflow = VideoChainWorkflow(api_key=self.test_api_key)
        prompts = workflow.generate_prompts("测试描述", num_segments=3)
        
        self.assertEqual(len(prompts), 3)
        
    @patch('video_chain.requests.post')
    def test_generate_video_segment_without_reference(self, mock_post):
        """Test video segment generation without reference image"""
        # Mock the API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [{"url": "https://example.com/video.mp4"}]
        }
        mock_post.return_value = mock_response
        
        # Mock the video download
        with patch('video_chain.requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.content = b"fake video content"
            
            workflow = VideoChainWorkflow(api_key=self.test_api_key)
            
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
                output_path = tmp.name
            
            try:
                result = workflow.generate_video_segment(
                    "测试提示词",
                    output_path=output_path
                )
                
                self.assertEqual(result, output_path)
                self.assertTrue(os.path.exists(output_path))
            finally:
                if os.path.exists(output_path):
                    os.unlink(output_path)
    
    @patch('video_chain.cv2.VideoCapture')
    @patch('video_chain.cv2.imwrite')
    def test_extract_last_frame(self, mock_imwrite, mock_capture):
        """Test extracting last frame from video"""
        # Mock video capture
        mock_cap = Mock()
        mock_cap.get.return_value = 100  # 100 frames
        mock_cap.read.return_value = (True, "fake_frame")
        mock_capture.return_value = mock_cap
        mock_imwrite.return_value = True
        
        workflow = VideoChainWorkflow(api_key=self.test_api_key)
        
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            output_path = tmp.name
        
        try:
            result = workflow.extract_last_frame("test_video.mp4", output_path)
            self.assertEqual(result, output_path)
            mock_imwrite.assert_called_once()
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_api_key_from_environment(self):
        """Test API key is read from environment variable"""
        os.environ['AIHUBMIX_API_KEY'] = "env-key-123"
        workflow = VideoChainWorkflow()
        self.assertEqual(workflow.api_key, "env-key-123")


class TestCLI(unittest.TestCase):
    """Test cases for CLI interface"""
    
    def test_cli_imports(self):
        """Test that CLI module can be imported"""
        import cli
        self.assertTrue(hasattr(cli, 'main'))


class TestWebApp(unittest.TestCase):
    """Test cases for web application"""
    
    def test_app_imports(self):
        """Test that app module can be imported"""
        import app
        self.assertTrue(hasattr(app, 'app'))
        
    def test_app_routes_exist(self):
        """Test that required routes exist"""
        import app
        
        # Get all route rules
        routes = [str(rule) for rule in app.app.url_map.iter_rules()]
        
        self.assertIn('/', routes)
        self.assertIn('/api/generate', routes)
        self.assertIn('/api/download/<path:video_path>', routes)
        self.assertIn('/api/status', routes)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
