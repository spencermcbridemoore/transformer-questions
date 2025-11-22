"""
Vast.ai instance lifecycle management.

Handles searching, launching, monitoring, and destroying Vast.ai instances.
"""
import time
import os
from typing import Optional, Dict, List, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from vastai import VastAI
except ImportError:
    raise ImportError("vastai-sdk not installed. Install with: pip install vastai-sdk")


class VastManager:
    """Manages Vast.ai instance lifecycle."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Vast.ai manager.
        
        Args:
            api_key: Vast.ai API key. If None, reads from VAST_API_KEY env var.
        """
        if api_key is None:
            api_key = os.getenv('VAST_API_KEY')
            if not api_key or api_key == 'your_vast_api_key_here':
                raise ValueError("VAST_API_KEY not found in .env file. Please set it first.")
        
        self.client = VastAI(api_key=api_key)
        self.instance_id: Optional[int] = None
        self.instance_start_time: Optional[float] = None
        self.selected_offer: Optional[Dict[str, Any]] = None
        
    def search_instances(
        self,
        gpu_type: str = "A100",
        max_price_per_hour: float = 1.5,
        limit: int = 50,
        gpu_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for available GPU instances.
        
        Args:
            gpu_type: GPU type to search for (e.g., "A100"). Ignored if gpu_types is provided.
            max_price_per_hour: Maximum price per hour in USD
            limit: Maximum number of offers to return
            gpu_types: List of GPU types to search for (e.g., ["A100", "H100"])
            
        Returns:
            List of offer dictionaries matching criteria
        """
        # Support multiple GPU types
        if gpu_types is None:
            gpu_types = [gpu_type]
        
        gpu_types_str = " or ".join(gpu_types)
        print(f"Searching for {gpu_types_str} instances under ${max_price_per_hour}/hour...")
        
        # Search for instances - search for all types and combine results
        all_offers = []
        for gpu in gpu_types:
            offers = self.client.search_offers(
                query=f"gpu_name:{gpu}",
                order="score",
                limit=limit
            )
            
            # Process offers - handle different return formats
            if offers is None:
                continue
            
            if isinstance(offers, list):
                available_offers = offers
            elif isinstance(offers, dict):
                available_offers = offers.get('offers', offers.get('instances', []))
                if not available_offers:
                    available_offers = [offers] if offers else []
            else:
                available_offers = []
            
            all_offers.extend(available_offers)
        
        # Remove duplicates by offer ID
        seen_ids = set()
        unique_offers = []
        for offer in all_offers:
            if isinstance(offer, dict):
                offer_id = offer.get('id')
                if offer_id and offer_id not in seen_ids:
                    seen_ids.add(offer_id)
                    unique_offers.append(offer)
        
        print(f"[INFO] Total offers received: {len(unique_offers)}")
        
        if not unique_offers:
            raise ValueError(f"No offers returned from API for {gpu_types_str}")
        
        # Filter by price and GPU type
        filtered_offers = []
        for offer in unique_offers:
            if not isinstance(offer, dict):
                continue
            
            price = offer.get('dph_total', offer.get('dph', offer.get('price', float('inf'))))
            gpu_name = offer.get('gpu_name', '')
            
            # Check if GPU name contains any of the target types
            matches_gpu = any(gpu.upper() in gpu_name.upper() for gpu in gpu_types)
            
            if matches_gpu and price < max_price_per_hour:
                filtered_offers.append(offer)
        
        print(f"[INFO] Filtered offers matching criteria: {len(filtered_offers)}")
        
        if not filtered_offers:
            # Fallback: try without strict price filter
            print(f"[WARNING] No {gpu_types_str} instances found under ${max_price_per_hour}/hour")
            print("Trying fallback search...")
            
            fallback_offers = []
            for offer in unique_offers:
                if not isinstance(offer, dict):
                    continue
                gpu_name = offer.get('gpu_name', '')
                if any(gpu.upper() in gpu_name.upper() for gpu in gpu_types):
                    fallback_offers.append(offer)
            
            if fallback_offers:
                filtered_offers = fallback_offers
                print(f"[INFO] Found {len(filtered_offers)} {gpu_types_str} offers (without price filter)")
        
        if not filtered_offers:
            raise ValueError(f"No {gpu_types_str} instances found")
        
        # Sort by price ascending
        filtered_offers.sort(key=lambda x: x.get('dph_total', x.get('dph', x.get('price', float('inf')))))
        
        return filtered_offers
    
    def select_cheapest(self, offers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Select cheapest offer from list.
        
        Args:
            offers: List of offer dictionaries
            
        Returns:
            Selected offer dictionary
        """
        if not offers:
            raise ValueError("No offers provided")
        
        selected = offers[0]
        price = selected.get('dph_total', selected.get('dph', selected.get('price', 0)))
        
        print(f"[OK] Selected instance:")
        print(f"  GPU: {selected.get('gpu_name', 'Unknown')}")
        print(f"  Price: ${price:.2f}/hour")
        print(f"  Offer ID: {selected.get('id', 'N/A')}")
        if 'geolocation' in selected:
            print(f"  Location: {selected.get('geolocation', 'N/A')}")
        
        self.selected_offer = selected
        return selected
    
    def launch_instance(
        self,
        offer_id: Optional[int] = None,
        image: str = "pytorch/pytorch:latest",
        disk: int = 10
    ) -> int:
        """
        Launch an instance.
        
        Args:
            offer_id: Offer ID. If None, uses selected offer.
            image: Docker image to use
            disk: Disk space in GB
            
        Returns:
            Instance ID
        """
        if offer_id is None:
            if self.selected_offer is None:
                raise ValueError("No offer selected. Call select_cheapest() first.")
            offer_id = self.selected_offer.get('id')
        
        if offer_id is None:
            raise ValueError("Offer ID is required")
        
        print("Launching instance...")
        print("[WARNING] This will start billing immediately!")
        
        self.instance_start_time = time.time()
        
        try:
            instance = self.client.create_instance(
                id=offer_id,
                image=image,
                disk=disk,
            )
            
            # Extract instance ID from response
            if isinstance(instance, dict):
                instance_id = instance.get('new_contract') or instance.get('id')
            else:
                instance_id = instance
            
            if not instance_id:
                raise ValueError("Failed to get instance ID from create_instance response")
            
            self.instance_id = instance_id
            print(f"[OK] Instance created: {instance_id}")
            return instance_id
            
        except Exception as e:
            self.instance_start_time = None
            raise Exception(f"Failed to launch instance: {e}")
    
    def wait_for_ready(
        self,
        max_wait_time: int = 300,
        poll_interval: int = 10
    ) -> Dict[str, Any]:
        """
        Wait for instance to be ready.
        
        Args:
            max_wait_time: Maximum time to wait in seconds
            poll_interval: Time between status checks in seconds
            
        Returns:
            Instance info dictionary
        """
        if self.instance_id is None:
            raise ValueError("No instance launched. Call launch_instance() first.")
        
        print("Waiting for instance to be ready...")
        start_time = time.time()
        
        instance_info = None
        while time.time() - start_time < max_wait_time:
            try:
                instances = self.client.show_instances()
                
                # Find our instance
                if isinstance(instances, list):
                    instance_list = instances
                elif isinstance(instances, dict):
                    instance_list = instances.get('instances', [instances] if instances else [])
                else:
                    instance_list = []
                
                for inst in instance_list:
                    if isinstance(inst, dict) and str(inst.get('id')) == str(self.instance_id):
                        status = inst.get('status', inst.get('state', inst.get('actual_status', 'unknown')))
                        ip = inst.get('public_ipaddr', inst.get('ip'))
                        
                        # Print status periodically
                        if (time.time() - start_time) % (poll_interval * 3) < poll_interval:
                            print(f"  Status: {status}, IP: {ip}")
                        
                        # Consider ready if IP is assigned
                        if ip and ip != 'None' and ip.strip():
                            instance_info = inst
                            print(f"[OK] Instance is ready! Status: {status}, IP: {ip}")
                            break
                        elif status in ['running', 'ready', 'online', 'active']:
                            instance_info = inst
                            print(f"[OK] Instance is ready! Status: {status}")
                            break
                        elif status in ['error', 'failed', 'terminated']:
                            raise Exception(f"Instance failed with status: {status}")
                
                if instance_info:
                    break
                
                time.sleep(poll_interval)
                
            except Exception as e:
                print(f"[WARNING] Error checking status: {e}")
                time.sleep(poll_interval)
        
        if not instance_info:
            raise TimeoutError(f"Instance {self.instance_id} did not become ready within {max_wait_time} seconds")
        
        return instance_info
    
    def get_connection_info(self, instance_info: Dict[str, Any]) -> Dict[str, str]:
        """
        Extract connection information from instance info.
        
        Args:
            instance_info: Instance info dictionary
            
        Returns:
            Dictionary with host, port, username
        """
        return {
            'host': instance_info.get('public_ipaddr', instance_info.get('ip')),
            'port': str(instance_info.get('ssh_port', 22)),
            'username': instance_info.get('ssh_username', 'root'),
        }
    
    def destroy_instance(self) -> bool:
        """
        Destroy the current instance.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.instance_id:
            print("[WARNING] No instance ID to destroy")
            return False
        
        print(f"\n[CLEANUP] Attempting to destroy instance {self.instance_id}...")
        try:
            try:
                result = self.client.destroy_instance(id=self.instance_id)
                print(f"[OK] Instance {self.instance_id} destroyed")
                self.instance_id = None
                return True
            except AttributeError:
                try:
                    result = self.client.destroy_instances([self.instance_id])
                    print(f"[OK] Instance {self.instance_id} destroyed")
                    self.instance_id = None
                    return True
                except Exception as e:
                    print(f"[ERROR] Failed to destroy instance: {e}")
                    return False
        except Exception as e:
            print(f"[ERROR] Failed to destroy instance: {e}")
            return False
        finally:
            print("[WARNING] If instance still exists, verify in Vast.ai console!")
    
    def calculate_cost(self, hourly_price: Optional[float] = None) -> Optional[float]:
        """
        Calculate estimated cost based on runtime.
        
        Args:
            hourly_price: Hourly price. If None, uses selected offer price.
            
        Returns:
            Estimated cost in USD, or None if cannot calculate
        """
        if self.instance_start_time is None:
            return None
        
        if hourly_price is None:
            if self.selected_offer:
                hourly_price = self.selected_offer.get('dph_total', self.selected_offer.get('dph', 0))
            else:
                return None
        
        runtime_seconds = time.time() - self.instance_start_time
        runtime_hours = runtime_seconds / 3600
        cost = runtime_hours * hourly_price
        
        return cost

