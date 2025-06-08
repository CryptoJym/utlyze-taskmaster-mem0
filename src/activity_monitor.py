#!/usr/bin/env python3
"""
Activity Monitor for Utlyze Taskmaster-Mem0
Passively collects development activity and syncs to Mem0
"""

import os
import sys
import time
import json
import threading
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import mem0 client
from mem0_client import UtlyzeMem0Client


class ActivityMonitor:
    """Monitors development activity and syncs to Mem0"""
    
    def __init__(self, watch_interval: int = 60):
        """
        Initialize the activity monitor
        
        Args:
            watch_interval: How often to collect activity (seconds)
        """
        self.watch_interval = watch_interval
        self.mem0_client = UtlyzeMem0Client()
        self.last_activity = {}
        self.running = False
        self.thread = None
        
    def get_git_info(self, cwd: str) -> Dict[str, str]:
        """Get current git branch and status"""
        try:
            # Get current branch
            branch = subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=cwd,
                stderr=subprocess.DEVNULL
            ).decode().strip()
            
            # Get last commit
            commit = subprocess.check_output(
                ["git", "log", "-1", "--oneline"],
                cwd=cwd,
                stderr=subprocess.DEVNULL
            ).decode().strip()
            
            # Check if dirty
            status = subprocess.check_output(
                ["git", "status", "--porcelain"],
                cwd=cwd,
                stderr=subprocess.DEVNULL
            ).decode().strip()
            
            return {
                "branch": branch,
                "last_commit": commit,
                "is_dirty": len(status) > 0,
                "modified_files": len(status.splitlines()) if status else 0
            }
        except Exception:
            return {}
    
    def get_open_files(self) -> List[str]:
        """Get list of recently modified files in current directory"""
        try:
            cwd = os.getcwd()
            recent_files = []
            
            # Find files modified in last hour
            for root, dirs, files in os.walk(cwd):
                # Skip hidden directories
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for file in files:
                    if file.startswith('.'):
                        continue
                        
                    filepath = os.path.join(root, file)
                    try:
                        mtime = os.path.getmtime(filepath)
                        if time.time() - mtime < 3600:  # Last hour
                            relative_path = os.path.relpath(filepath, cwd)
                            recent_files.append(relative_path)
                    except:
                        continue
            
            return recent_files[:10]  # Limit to 10 most recent
        except Exception as e:
            logger.error(f"Error getting open files: {e}")
            return []
    
    def get_terminal_context(self) -> Dict[str, Any]:
        """Get current terminal context"""
        cwd = os.getcwd()
        
        context = {
            "cwd": cwd,
            "project": os.path.basename(cwd),
            "timestamp": datetime.now().isoformat(),
            "user": os.getenv("USER", "unknown"),
            "shell": os.getenv("SHELL", "unknown"),
            "recent_files": self.get_open_files()
        }
        
        # Add git info if in a git repo
        git_info = self.get_git_info(cwd)
        if git_info:
            context["git"] = git_info
        
        # Check for Python virtual environment
        if os.getenv("VIRTUAL_ENV"):
            context["virtual_env"] = os.path.basename(os.getenv("VIRTUAL_ENV"))
        
        # Check for Node.js project
        if os.path.exists("package.json"):
            context["node_project"] = True
            
        # Check for Python project
        if os.path.exists("requirements.txt") or os.path.exists("pyproject.toml"):
            context["python_project"] = True
        
        return context
    
    def has_activity_changed(self, current: Dict[str, Any]) -> bool:
        """Check if activity has meaningfully changed"""
        if not self.last_activity:
            return True
        
        # Check if directory changed
        if current.get("cwd") != self.last_activity.get("cwd"):
            return True
        
        # Check if git branch changed
        if current.get("git", {}).get("branch") != self.last_activity.get("git", {}).get("branch"):
            return True
        
        # Check if files have been modified
        current_files = set(current.get("recent_files", []))
        last_files = set(self.last_activity.get("recent_files", []))
        
        if current_files != last_files:
            return True
        
        # Check if git status changed significantly
        if current.get("git", {}).get("is_dirty") != self.last_activity.get("git", {}).get("is_dirty"):
            return True
        
        return False
    
    def sync_activity(self):
        """Sync current activity to Mem0"""
        try:
            context = self.get_terminal_context()
            
            # Only sync if activity has changed
            if not self.has_activity_changed(context):
                logger.debug("No significant activity change, skipping sync")
                return
            
            # Create activity memory
            activity_description = f"""
            Development Activity Update:
            - Working in: {context['project']} ({context['cwd']})
            - Git branch: {context.get('git', {}).get('branch', 'N/A')}
            - Recent files: {', '.join(context['recent_files'][:5]) if context['recent_files'] else 'None'}
            - Git status: {'Modified files' if context.get('git', {}).get('is_dirty') else 'Clean'}
            - Time: {context['timestamp']}
            """
            
            # Add to Mem0
            messages = [{"role": "user", "content": activity_description}]
            result = self.mem0_client.client.add(
                messages,
                user_id="utlyze",
                metadata={
                    "type": "development_activity",
                    "source": "activity_monitor",
                    "project": context['project'],
                    "git_branch": context.get('git', {}).get('branch'),
                    "timestamp": context['timestamp']
                }
            )
            
            logger.info(f"Activity synced: {context['project']} on {context.get('git', {}).get('branch', 'N/A')}")
            self.last_activity = context
            
        except Exception as e:
            logger.error(f"Error syncing activity: {e}")
    
    def monitor_loop(self):
        """Main monitoring loop"""
        logger.info("Activity monitor started")
        
        while self.running:
            try:
                self.sync_activity()
                time.sleep(self.watch_interval)
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Monitor error: {e}")
                time.sleep(self.watch_interval)
        
        logger.info("Activity monitor stopped")
    
    def start(self):
        """Start the activity monitor in background"""
        if self.running:
            logger.warning("Monitor already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.thread.start()
        logger.info("Activity monitor started in background")
    
    def stop(self):
        """Stop the activity monitor"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Activity monitor stopped")
    
    def run_once(self):
        """Run a single activity sync"""
        self.sync_activity()


def main():
    """Run activity monitor as standalone process"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Utlyze Activity Monitor")
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Sync interval in seconds (default: 60)"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run once and exit"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon process"
    )
    
    args = parser.parse_args()
    
    # Check API key
    if not os.getenv("MEM0_API_KEY"):
        print("Error: MEM0_API_KEY environment variable not set")
        sys.exit(1)
    
    monitor = ActivityMonitor(watch_interval=args.interval)
    
    if args.once:
        monitor.run_once()
    elif args.daemon:
        # Daemonize the process
        try:
            pid = os.fork()
            if pid > 0:
                # Parent process
                print(f"Activity monitor started with PID: {pid}")
                sys.exit(0)
        except OSError as e:
            print(f"Fork failed: {e}")
            sys.exit(1)
        
        # Child process continues
        monitor.monitor_loop()
    else:
        # Run in foreground
        try:
            monitor.monitor_loop()
        except KeyboardInterrupt:
            print("\nShutting down activity monitor...")


if __name__ == "__main__":
    main()