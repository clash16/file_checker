**目录校验工具**
===

这是一个基于Python语言制作的目录校验工具，算法为SHA256。
使用命令行调用，原文件大小为5KB，单个程序封装后大小为6.57MB。
如果你的项目语言为Python可以考虑使用这个模块进行文件校验。

特点：
1、使用命令行，方便其他项目调用。
2、多线程分块，大幅度提高硬件资源利用率，加快校验速度。
3、导出文件为已经压缩过的校验文件，降低校验文件的容量占用。

制作：使用ChatGPT生成。

用法：
core.py {export,import} -d DIRECTOR -f FILE [-l ERROR-LOG] [-t THREADS] 

导出模式
core.py export -d 被校验的目录 -f 导出的校验文件 -l 错误日志 -t 线程
例如：我需要将C:\FinalShell校验，导出校验文件为C:\Users\Administrator\Desktop\FinalShell.filecheck 如果有错误就将日志保存为 C:\Users\Administrator\Desktop\error.log 线程为8个
则命令为  core.py export -d C:\FinalShell -f C:\Users\Administrator\Desktop\FinalShell.filecheck -l C:\Users\Administrator\Desktop\error.log  -t 8

导入模式
core.py import -d 被校验的目录 -f 导出的校验文件 -l 错误日志 -t 线程
例如：我需要将C:\FinalShell校验，导入校验文件为C:\Users\Administrator\Desktop\FinalShell.filecheck 如果有错误就将日志保存为 C:\Users\Administrator\Desktop\error.log 线程为8个
则命令为  core.py import -d C:\FinalShell -f C:\Users\Administrator\Desktop\FinalShell.filecheck -l C:\Users\Administrator\Desktop\error.log  -t 8

**导出模式**的输出显示

[INFO] Found 326 files to process.
[INFO] Export completed. Results saved to C:\Users\Administrator\Desktop\FinalShell.filecheck

**导入模式**的输出显示

如果一切**正常**，被校验的目录任何文件完整并哈希值正确，则会打印
[INFO] Starting validation...
[INFO] Validation completed. Errors found: 0
[INFO] All files are validated successfully.

如果被校验的目录有一些文件**遗失**，则会打印

示例1
[INFO] Starting validation...
MISSING: ipdata.dat
[INFO] Validation completed. Errors found: 1
[ERROR] Validation errors were logged to C:\Users\Administrator\Desktop\error.log

示例2
[INFO] Starting validation...
MISSING: img\logo.icns
MISSING: sync\deletions.json
[INFO] Validation completed. Errors found: 2
[ERROR] Validation errors were logged to C:\Users\Administrator\Desktop\error.log

提示丢失的文件，并且丢失在哪一个目录中。
丢失文件若过多，可以在指定的错误文件中查询到。

在error.log中
2024-12-19 20:40:16,622 - ERROR - MISSING: ipdata.dat
2024-12-19 20:41:00,137 - ERROR - MISSING: img\logo.icns
2024-12-19 20:41:00,168 - ERROR - MISSING: sync\deletions.json

若被校验的目录中有一些文件**哈希值不正确**，则会打印
[INFO] Starting validation...
HASH MISMATCH: finalshelltest.bat (expected: c67a12da71af96c47777544eea6c75fe2e56ddc798e20ca47cc5c9a3fe5f4657, got: 3adb96f43415eaa47d0fb18b08be10119ebc89f12c7aaa6ad22160678f6ae040)
[INFO] Validation completed. Errors found: 1
[ERROR] Validation errors were logged to C:\Users\Administrator\Desktop\error.log

在error.log中输出为
2024-12-19 20:43:46,936 - ERROR - HASH MISMATCH: finalshelltest.bat (expected: c67a12da71af96c47777544eea6c75fe2e56ddc798e20ca47cc5c9a3fe5f4657, got: 3adb96f43415eaa47d0fb18b08be10119ebc89f12c7aaa6ad22160678f6ae040)
