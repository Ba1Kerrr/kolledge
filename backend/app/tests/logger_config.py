import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

class TestLogger:
    """Класс для создания логгеров тестов"""
    
    LOG_DIR = Path(__file__).parent / "logs"
    
    @staticmethod
    def get_logger(test_file_name: str) -> logging.Logger:
        """Создает логгер для конкретного тестового файла"""
        
        # Создаем имя логгера на основе имени файла
        file_stem = Path(test_file_name).stem
        logger_name = f"test_{file_stem}"
        
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        
        if logger.handlers:
            return logger
        
        TestLogger.LOG_DIR.mkdir(exist_ok=True)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        log_file = TestLogger.LOG_DIR / f"{file_stem}.log"
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)
        logger.addHandler(console_handler)
        
        return logger
    
    @staticmethod
    def log_error(logger: logging.Logger, error_msg: str, exception: Exception = None):
        """Логирует ошибку с traceback"""
        logger.error(error_msg)
        if exception:
            logger.error(f"Exception: {str(exception)}")
            import traceback
            logger.error(f"Traceback:\n{traceback.format_exc()}")
    
    @staticmethod
    def log_test_result(logger: logging.Logger, test_name: str, success: bool, details: str = ""):
        """Логирует результат теста"""
        status = "ПРОЙДЕН" if success else "ПРОВАЛЕН"
        logger.info(f"Тест '{test_name}': {status}")
        if details:
            logger.info(f"Детали: {details}")