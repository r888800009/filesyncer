# filesyncer

## Install
```bash
git clone https://github.com/r888800009/filesyncer
cd filesyncer
pip install .
```

## feature
- [x] keep file mtimes (by rsync)

## Usage
```
syncer init
syncer pull
syncer push
syncer mv <src> <dst>
syncer rm <path>
syncer remote add <name> <0.0.0.0:/path/to/dir>
```

use `syncer -h` to see more details

## MEMO
- [ ] safe delete?
    - `--dry-run` 其實是不夠的，可能在 dry-run 之後，remote 如果重新 mount file system 卻失敗(empty dir)，那就會刪除掉本地的檔案
- [ ] unit test: current unit test not implemented yet
