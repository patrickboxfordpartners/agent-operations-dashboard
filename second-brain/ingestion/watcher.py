"""File system watcher for automatic project ingestion"""
import asyncio
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from shared.config import config
from shared.monitoring import logger
from ingestion.processor import ingestor

class ProjectWatcher(FileSystemEventHandler):
    """Watches for new project folders and triggers ingestion"""

    def __init__(self):
        self.queue = asyncio.Queue()

    def on_created(self, event):
        """Triggered when new folder is created"""

        if event.is_directory:
            folder_path = Path(event.src_path)
            logger.info(f"New project folder detected: {folder_path}")

            # Add to queue for async processing
            asyncio.create_task(self._process_queued(folder_path))

    async def _process_queued(self, folder_path: Path):
        """Process project from queue"""

        # Wait a bit for files to finish copying
        await asyncio.sleep(2)

        try:
            project_id = await ingestor.process_project(folder_path)
            logger.info(f"✅ Auto-ingested: {project_id}")

        except Exception as e:
            logger.error(f"Failed to ingest {folder_path}: {e}")

def main():
    """Run watcher as standalone service"""

    watch_path = config.STORAGE_PATH
    watch_path.mkdir(parents=True, exist_ok=True)

    logger.info(f"Starting project watcher on: {watch_path}")
    logger.info("Drop new project folders here to auto-ingest them.")

    observer = Observer()
    observer.schedule(ProjectWatcher(), path=str(watch_path), recursive=False)
    observer.start()

    try:
        # Keep running
        while True:
            asyncio.get_event_loop().run_until_complete(asyncio.sleep(1))
    except KeyboardInterrupt:
        observer.stop()
        logger.info("Watcher stopped")

    observer.join()

if __name__ == "__main__":
    main()
