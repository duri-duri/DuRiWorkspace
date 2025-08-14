from DuRiCore.trace import emit_trace
import logging
import sys

def setup_logging():
    """Setup consistent logging format for the application"""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s :: %(message)s', handlers=[logging.StreamHandler(sys.stdout)])
    logging.getLogger('core').setLevel(logging.INFO)
    logging.getLogger('adapters').setLevel(logging.INFO)
    return logging.getLogger(__name__)
logger = setup_logging()