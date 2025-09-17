"""
ML Services for image analysis and alternative text generation.
"""
import os
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path
import requests
from PIL import Image
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration, YolosImageProcessor, YolosForObjectDetection

logger = logging.getLogger(__name__)

class MLImageAnalyzer:
    """ML service for image analysis including caption generation and object detection."""
    
    def __init__(self):
        self.caption_model = None
        self.caption_processor = None
        self.detection_model = None
        self.detection_processor = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")
    
    def _load_caption_model(self):
        """Load the BLIP model for image captioning."""
        if self.caption_model is None:
            try:
                model_name = "Salesforce/blip-image-captioning-base"
                self.caption_processor = BlipProcessor.from_pretrained(model_name)
                self.caption_model = BlipForConditionalGeneration.from_pretrained(model_name)
                self.caption_model.to(self.device)
                logger.info("Caption model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load caption model: {e}")
                raise
    
    def _load_detection_model(self):
        """Load the YOLOS model for object detection."""
        if self.detection_model is None:
            try:
                model_name = "hustvl/yolos-tiny"
                self.detection_processor = YolosImageProcessor.from_pretrained(model_name)
                self.detection_model = YolosForObjectDetection.from_pretrained(model_name)
                self.detection_model.to(self.device)
                logger.info("Detection model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load detection model: {e}")
                raise
    
    def generate_alt_text(self, image_path: str) -> str:
        """
        Generate alternative text for an image using BLIP model.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Generated alternative text
        """
        try:
            self._load_caption_model()
            
            # Load and process image
            image = Image.open(image_path).convert('RGB')
            inputs = self.caption_processor(image, return_tensors="pt").to(self.device)
            
            # Generate caption
            with torch.no_grad():
                out = self.caption_model.generate(**inputs, max_length=50, num_beams=5)
            
            caption = self.caption_processor.decode(out[0], skip_special_tokens=True)
            logger.info(f"Generated caption for {image_path}: {caption}")
            return caption
            
        except Exception as e:
            logger.error(f"Error generating alt text for {image_path}: {e}")
            return "Image description unavailable"
    
    def detect_objects(self, image_path: str) -> List[Dict[str, Any]]:
        """
        Detect objects in an image using YOLOS model.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            List of detected objects with labels and confidence scores
        """
        try:
            self._load_detection_model()
            
            # Load and process image
            image = Image.open(image_path).convert('RGB')
            inputs = self.detection_processor(images=image, return_tensors="pt").to(self.device)
            
            # Detect objects
            with torch.no_grad():
                outputs = self.detection_model(**inputs)
            
            # Process results
            target_sizes = torch.tensor([image.size[::-1]]).to(self.device)
            results = self.detection_processor.post_process_object_detection(
                outputs, target_sizes=target_sizes, threshold=0.5
            )[0]
            
            objects = []
            for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
                objects.append({
                    "label": self.detection_model.config.id2label[label.item()],
                    "confidence": score.item(),
                    "box": box.tolist()
                })
            
            logger.info(f"Detected {len(objects)} objects in {image_path}")
            return objects
            
        except Exception as e:
            logger.error(f"Error detecting objects in {image_path}: {e}")
            return []
    
    def get_searchable_keywords(self, image_path: str) -> List[str]:
        """
        Extract searchable keywords from an image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            List of searchable keywords
        """
        objects = self.detect_objects(image_path)
        keywords = [obj["label"] for obj in objects if obj["confidence"] > 0.5]
        
        # Also add caption words as keywords
        caption = self.generate_alt_text(image_path)
        caption_words = [word.lower().strip('.,!?') for word in caption.split() 
                        if len(word) > 2 and word.isalpha()]
        keywords.extend(caption_words)
        
        # Remove duplicates and return
        return list(set(keywords))

# Global instance
ml_analyzer = MLImageAnalyzer()