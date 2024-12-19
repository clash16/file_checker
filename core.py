import os
import hashlib
import argparse
import json
import gzip
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

# 模块化配置
CHUNK_SIZE = 8192  # 分块大小，比如 8KB
DEFAULT_THREAD_COUNT = 4  # 默认线程数

# 设置日志系统
def setup_logger(log_file: str):
    logging.basicConfig(
        filename=log_file,
        level=logging.ERROR,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    console = logging.StreamHandler()
    console.setLevel(logging.ERROR)
    logging.getLogger().addHandler(console)

def calculate_file_hash(file_path: Path, chunk_size: int = CHUNK_SIZE) -> str:
    """
    计算文件的SHA256哑值
    """
    sha256 = hashlib.sha256()
    try:
        with file_path.open('rb') as f:
            while chunk := f.read(chunk_size):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception as e:
        logging.error(f"Error calculating hash for {file_path}: {e}")
        return None

def export_file_hashes(directory: Path, output_file: Path, thread_count: int):
    """
    导出模式：对指定目录进行遍历，并导出每个文件的索引和哑值。
    """
    files_to_process = [file for file in directory.rglob('*') if file.is_file()]
    result = {}

    print(f"[INFO] Found {len(files_to_process)} files to process.")

    with ThreadPoolExecutor(max_workers=thread_count) as executor:
        future_to_file = {executor.submit(calculate_file_hash, file): file for file in files_to_process}
        for future in as_completed(future_to_file):
            file = future_to_file[future]
            hash_value = future.result()
            if hash_value:
                relative_path = str(file.relative_to(directory))
                result[relative_path] = hash_value

    # 将结果写入压缩文件
    try:
        with gzip.open(output_file, 'wt', encoding='utf-8') as f:
            json.dump(result, f, separators=(',', ':'))  # 最大压缩
        print(f"[INFO] Export completed. Results saved to {output_file}")
    except Exception as e:
        logging.error(f"Error writing to export file: {e}")

def import_and_validate(directory: Path, input_file: Path, log_file: Path, thread_count: int):
    """
    导入模式：校验文件目录的索引和哑值，输出错误日志。
    """
    # 读取压缩的JSON文件
    try:
        with gzip.open(input_file, 'rt', encoding='utf-8') as f:
            expected_data = json.load(f)
    except Exception as e:
        logging.error(f"Error reading import file: {e}")
        return

    errors = []
    print("[INFO] Starting validation...")

    def validate_file(relative_path: str, expected_hash: str):
        file_path = directory / relative_path
        if not file_path.exists():
            error_message = f"MISSING: {relative_path}"
            errors.append(error_message)
            logging.error(error_message)
        else:
            actual_hash = calculate_file_hash(file_path)
            if actual_hash != expected_hash:
                error_message = f"HASH MISMATCH: {relative_path} (expected: {expected_hash}, got: {actual_hash})"
                errors.append(error_message)
                logging.error(error_message)

    # 使用多线程校验
    with ThreadPoolExecutor(max_workers=thread_count) as executor:
        futures = [executor.submit(validate_file, path, hash_value) for path, hash_value in expected_data.items()]
        for future in as_completed(futures):
            future.result()  # 为了捕获异常

    print(f"[INFO] Validation completed. Errors found: {len(errors)}")
    if errors:
        print(f"[ERROR] Validation errors were logged to {log_file}")
    else:
        print("[INFO] All files are validated successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="File Validation Tool")
    parser.add_argument("mode", choices=["export", "import"], help="Mode: 'export' or 'import'")
    parser.add_argument("-d", "--directory", required=True, help="Target directory for files")
    parser.add_argument("-f", "--file", required=True, help="Export or import file path")
    parser.add_argument("-l", "--log", default="error.log", help="Log file path (for import mode)")
    parser.add_argument("-t", "--threads", type=int, default=DEFAULT_THREAD_COUNT, help="Number of threads")

    args = parser.parse_args()

    target_directory = Path(args.directory)
    target_file = Path(args.file)
    log_file = Path(args.log)

    if not target_directory.exists():
        print("[ERROR] Target directory does not exist.")
        exit(1)

    if args.mode == "export":
        export_file_hashes(target_directory, target_file, args.threads)
    elif args.mode == "import":
        setup_logger(log_file)
        import_and_validate(target_directory, target_file, log_file, args.threads)
