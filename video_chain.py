"""
Video Chain Workflow - Core module for generating coherent video segments
"""
import os
import time
import json
import base64
import requests
from pathlib import Path
from typing import List, Dict, Optional
from openai import OpenAI
import cv2
from PIL import Image
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class VideoChainWorkflow:
    """
    A workflow that generates a long video from multiple segments.
    Each segment is generated using Sora-2 API with prompts from Gemini-3-pro-preview.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the VideoChainWorkflow.
        
        Args:
            api_key: aihubmix API key. If not provided, reads from AIHUBMIX_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("AIHUBMIX_API_KEY")
        if not self.api_key:
            raise ValueError("API key is required. Set AIHUBMIX_API_KEY environment variable or pass api_key parameter.")
        
        self.base_url = "https://aihubmix.com/v1"
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
    def generate_prompts(self, user_description: str, reference_image_path: Optional[str] = None, 
                        num_segments: int = 3) -> List[str]:
        """
        Generate video segment prompts using Gemini-3-pro-preview.
        
        Args:
            user_description: User's description of the desired video
            reference_image_path: Optional path to reference image
            num_segments: Number of video segments to generate
            
        Returns:
            List of prompts for each video segment
        """
        print(f"正在生成 {num_segments} 个视频片段的提示词...")
        
        # Prepare the prompt for Gemini
        system_prompt = f"""你是一个专业的视频分镜脚本生成助手。
根据用户的需求描述，生成 {num_segments} 个连贯的视频片段的详细文字提示词。
每个提示词应该：
1. 详细描述画面内容、动作、场景
2. 确保片段之间有连贯性和过渡
3. 使用中文
4. 适合用于视频生成模型

请以JSON格式返回，格式为：
{{"segments": ["提示词1", "提示词2", "提示词3", ...]}}
"""
        
        content = [
            {"type": "input_text", "text": f"{system_prompt}\n\n用户需求：{user_description}"}
        ]
        
        # Add reference image if provided
        if reference_image_path and os.path.exists(reference_image_path):
            # Read and encode image
            with open(reference_image_path, "rb") as img_file:
                img_data = base64.b64encode(img_file.read()).decode('utf-8')
            content.append({
                "type": "input_image",
                "image_url": f"data:image/jpeg;base64,{img_data}"
            })
        
        try:
            response = self.client.responses.create(
                model="gemini-3-pro-preview",
                input=[
                    {
                        "role": "user",
                        "content": content
                    }
                ]
            )
            
            # Parse the response
            response_text = response.output[0].content
            print(f"Gemini响应: {response_text}")
            
            # Try to extract JSON from the response
            try:
                # Find JSON in the response
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                if start_idx != -1 and end_idx > start_idx:
                    json_str = response_text[start_idx:end_idx]
                    prompts_data = json.loads(json_str)
                    prompts = prompts_data.get("segments", [])
                else:
                    # Fallback: split by newlines
                    prompts = [line.strip() for line in response_text.split('\n') 
                              if line.strip() and not line.strip().startswith('{') 
                              and not line.strip().startswith('}')][:num_segments]
            except json.JSONDecodeError:
                # Fallback: split the response into segments
                prompts = [line.strip() for line in response_text.split('\n') 
                          if line.strip()][:num_segments]
            
            # Ensure we have the right number of prompts
            while len(prompts) < num_segments:
                prompts.append(f"{user_description} - 片段 {len(prompts) + 1}")
            
            print(f"生成了 {len(prompts)} 个提示词")
            for i, prompt in enumerate(prompts, 1):
                print(f"  片段 {i}: {prompt[:50]}...")
            
            return prompts[:num_segments]
            
        except Exception as e:
            print(f"生成提示词时出错: {e}")
            # Fallback to simple prompts
            return [f"{user_description} - 片段 {i+1}" for i in range(num_segments)]
    
    def generate_video_segment(self, prompt: str, reference_image_path: Optional[str] = None,
                              size: str = "1280x720", seconds: int = 4, 
                              output_path: Optional[str] = None) -> str:
        """
        Generate a video segment using Sora-2 API.
        
        Args:
            prompt: Text prompt for video generation
            reference_image_path: Optional path to reference image
            size: Video size (e.g., "1280x720", "720x1280")
            seconds: Video duration in seconds
            output_path: Optional path to save the video
            
        Returns:
            Path to the generated video file
        """
        print(f"正在生成视频片段: {prompt[:50]}...")
        
        url = f"{self.base_url}/videos"
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            if reference_image_path and os.path.exists(reference_image_path):
                # Determine MIME type from file extension
                import mimetypes
                mime_type, _ = mimetypes.guess_type(reference_image_path)
                if not mime_type or not mime_type.startswith('image/'):
                    mime_type = "image/jpeg"  # Fallback
                
                # Generate with reference image
                with open(reference_image_path, "rb") as img_file:
                    files = {
                        "prompt": (None, prompt),
                        "model": (None, "sora-2"),  # Use consistent model name
                        "size": (None, size),
                        "seconds": (None, str(seconds)),
                        "input_reference": (
                            os.path.basename(reference_image_path),
                            img_file,
                            mime_type
                        )
                    }
                    
                    response = requests.post(url, headers=headers, files=files)
            else:
                # Generate without reference image
                headers["Content-Type"] = "application/json"
                payload = {
                    "model": "sora-2",
                    "prompt": prompt,
                    "size": size,
                    "seconds": str(seconds),
                }
                
                response = requests.post(url, headers=headers, json=payload)
            
            print(f"API响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"API响应: {result}")
                
                # The API should return a video URL or video data
                # This is a placeholder - adjust based on actual API response format
                if "data" in result:
                    video_url = result["data"][0].get("url") if isinstance(result["data"], list) else result["data"].get("url")
                elif "url" in result:
                    video_url = result["url"]
                else:
                    print(f"未预期的API响应格式: {result}")
                    return None
                
                # Download the video
                if video_url:
                    video_response = requests.get(video_url)
                    
                    # Check if download was successful
                    if video_response.status_code != 200:
                        print(f"下载视频失败，状态码: {video_response.status_code}")
                        return None
                    
                    if output_path is None:
                        output_path = f"segment_{int(time.time())}.mp4"
                    
                    with open(output_path, "wb") as f:
                        f.write(video_response.content)
                    
                    print(f"视频已保存到: {output_path}")
                    return output_path
            else:
                print(f"生成视频失败: {response.text}")
                return None
                
        except Exception as e:
            print(f"生成视频时出错: {e}")
            return None
    
    def extract_last_frame(self, video_path: str, output_path: Optional[str] = None) -> str:
        """
        Extract the last frame from a video file.
        
        Args:
            video_path: Path to the video file
            output_path: Optional path to save the frame image
            
        Returns:
            Path to the extracted frame image
        """
        print(f"正在提取视频最后一帧: {video_path}")
        
        try:
            cap = cv2.VideoCapture(video_path)
            
            # Get total number of frames
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Set to last frame
            cap.set(cv2.CAP_PROP_POS_FRAMES, total_frames - 1)
            
            # Read the frame
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                if output_path is None:
                    output_path = f"frame_{int(time.time())}.jpg"
                
                cv2.imwrite(output_path, frame)
                print(f"帧已保存到: {output_path}")
                return output_path
            else:
                print("无法读取视频帧")
                return None
                
        except Exception as e:
            print(f"提取帧时出错: {e}")
            return None
    
    def concatenate_videos(self, video_paths: List[str], output_path: str = "final_video.mp4") -> str:
        """
        Concatenate multiple video files into one.
        
        Args:
            video_paths: List of paths to video files
            output_path: Path to save the final concatenated video
            
        Returns:
            Path to the concatenated video
        """
        print(f"正在合并 {len(video_paths)} 个视频片段...")
        
        try:
            from moviepy.editor import VideoFileClip, concatenate_videoclips
            
            # Load all video clips
            clips = []
            for video_path in video_paths:
                if os.path.exists(video_path):
                    clip = VideoFileClip(video_path)
                    clips.append(clip)
                else:
                    print(f"警告: 视频文件不存在: {video_path}")
            
            if not clips:
                print("没有可用的视频片段进行合并")
                return None
            
            # Concatenate clips
            final_clip = concatenate_videoclips(clips)
            
            # Write the result
            final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')
            
            # Close all clips
            for clip in clips:
                clip.close()
            final_clip.close()
            
            print(f"最终视频已保存到: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"合并视频时出错: {e}")
            return None
    
    def run_workflow(self, user_description: str, reference_image_path: Optional[str] = None,
                    num_segments: int = 3, size: str = "1280x720", seconds_per_segment: int = 4,
                    output_dir: str = "output") -> Optional[str]:
        """
        Run the complete video chain workflow.
        
        Args:
            user_description: User's description of the desired video
            reference_image_path: Optional path to initial reference image
            num_segments: Number of video segments to generate
            size: Video size (e.g., "1280x720")
            seconds_per_segment: Duration of each segment in seconds
            output_dir: Directory to save output files
            
        Returns:
            Path to the final concatenated video
        """
        print("\n=== 开始视频链工作流 ===\n")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Step 1: Generate prompts
        prompts = self.generate_prompts(user_description, reference_image_path, num_segments)
        
        # Step 2: Generate video segments
        video_segments = []
        current_reference = reference_image_path
        
        for i, prompt in enumerate(prompts, 1):
            print(f"\n--- 生成片段 {i}/{num_segments} ---")
            
            segment_path = os.path.join(output_dir, f"segment_{i}.mp4")
            video_path = self.generate_video_segment(
                prompt=prompt,
                reference_image_path=current_reference,
                size=size,
                seconds=seconds_per_segment,
                output_path=segment_path
            )
            
            if video_path and os.path.exists(video_path):
                video_segments.append(video_path)
                
                # Extract last frame for next segment (if not the last segment)
                if i < num_segments:
                    frame_path = os.path.join(output_dir, f"frame_{i}.jpg")
                    current_reference = self.extract_last_frame(video_path, frame_path)
                    
                    if not current_reference:
                        print(f"警告: 无法提取片段 {i} 的最后一帧，将不使用参考图片")
                        current_reference = None
            else:
                print(f"警告: 片段 {i} 生成失败")
            
            # Add a small delay to avoid rate limiting
            time.sleep(2)
        
        # Step 3: Concatenate all segments
        if video_segments:
            print(f"\n--- 合并所有片段 ---")
            final_video_path = os.path.join(output_dir, "final_video.mp4")
            result = self.concatenate_videos(video_segments, final_video_path)
            
            print("\n=== 工作流完成 ===\n")
            return result
        else:
            print("\n=== 工作流失败: 没有生成任何视频片段 ===\n")
            return None
