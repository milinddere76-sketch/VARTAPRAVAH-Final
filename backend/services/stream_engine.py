import os
import redis
import time
import subprocess
import config

class StreamEngine:
    def __init__(self):
        self.promo_path = os.path.join(config.ASSETS_DIR, "promo.mp4")
        self.emergency_loop = os.path.join(config.ASSETS_DIR, "emergency_loop.mp4")
        self.r = redis.Redis(host=config.REDIS_HOST, port=int(config.REDIS_PORT))
        self.last_ad_time = 0
        self.fail_count = 0

    def stream_to_youtube(self, video_path, node_name="PRIMARY"):
        """
        Pushes the video to YouTube Live RTMP.
        """
        stream_key = config.STREAM_KEY
        if not stream_key:
             return False

        # Enterprise Failover Logic: Using Backup RTMP if Primary is problematic
        rtmp_url = f"rtmp://a.rtmp.youtube.com/live2/{stream_key}"
        if self.fail_count > 3:
            print("⚠️ [FAILOVER] Primary RTMP endpoint unstable. Switching to BACKUP RTMP...")
            rtmp_url = f"rtmp://b.rtmp.youtube.com/live2/{stream_key}"

        cmd = [
            "ffmpeg", "-y", "-re", "-i", video_path,
            "-c:v", "libx264", "-preset", "veryfast", "-maxrate", "3000k", "-bufsize", "6000k",
            "-pix_fmt", "yuv420p", "-g", "50", "-c:a", "aac", "-b:a", "128k",
            "-f", "flv", rtmp_url
        ]

        try:
            subprocess.run(cmd, check=True)
            self.fail_count = 0 # Reset on success
            return True
        except subprocess.CalledProcessError:
            self.fail_count += 1
            return False

    def switch_to_backup_server(self):
        """Logic for complete server-level failover."""
        print("🚨 [CRITICAL] Stream is DOWN. Initiating Auto-Failover Logic...")
        
        # 1. Try local emergency loop first (Zero-Silence)
        if os.path.exists(self.emergency_loop):
            print("🔄 [FAILOVER] Playing Local Emergency Loop...")
            self.stream_to_youtube(self.emergency_loop, node_name="EMERGENCY-NODE")
        else:
            print("🔄 [FAILOVER] Playing Brand Promo...")
            self.stream_to_youtube(self.promo_path, node_name="FAILOVER-NODE")

    def run(self):
        print("🏢 [ENTERPRISE] VARTAPRAVAH Auto-Failover Stream Engine Active.")
        
        while True:
            try:
                # Ad Insertion Logic
                if time.time() - self.last_ad_time > 300:
                    self.stream_to_youtube(self.promo_path)
                    self.last_ad_time = time.time()
                    continue

                # Normal Bulletin Flow
                ready_video = None
                try:
                    ready_video = self.r.lpop("ready_videos")
                except Exception as e:
                    print(f"⚠️ [REDIS] Primary Backend (Hetzner) unreachable: {e}")

                if ready_video:
                    target = ready_video.decode()
                    if not self.stream_to_youtube(target):
                        self.switch_to_backup_server()
                else:
                    # No news? Play promo and wait
                    if not self.stream_to_youtube(self.promo_path):
                        self.switch_to_backup_server()

            except Exception as e:
                print(f"⚠️ [SYSTEM] Engine Exception: {e}")
                self.switch_to_backup_server()
                time.sleep(5)

if __name__ == "__main__":
    engine = StreamEngine()
    engine.run()
