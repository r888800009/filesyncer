import argparse
import os
import subprocess
import yaml

REPOSITORY_METADATA_FILENAME = "./.r809filesyncer/repository.yaml"
REPOSITORY_METADATA_DIRNAME = os.path.dirname(REPOSITORY_METADATA_FILENAME)

RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
def colorize(color, text):
    return COLORS[color] + text + '\033[0m'

def check_rsync():
    try:
        subprocess.run(["rsync", "--version"], check=True, stdout=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        raise SystemExit("[!] rsync is not installed.")
    # print("[+] rsync is installed.")

def check_init():
    if not os.path.exists(REPOSITORY_METADATA_FILENAME):
        raise SystemExit("[!] This directory is not a syncer repository.")

def init(args):
    if os.path.exists(REPOSITORY_METADATA_DIRNAME):
        raise SystemExit("[!] This directory is already a syncer repository.")
    else:
        os.makedirs(REPOSITORY_METADATA_DIRNAME)
        with open(REPOSITORY_METADATA_FILENAME, "w") as f:
            yaml.dump({"remotes": []}, f)
        print("[+] Initialized syncer repository.")
    
def load_repository_metadata():
    with open(REPOSITORY_METADATA_FILENAME, "r") as f:
        return yaml.load(f, Loader=yaml.FullLoader)

def save_repository_metadata(repository_metadata):
    with open(REPOSITORY_METADATA_FILENAME, "w") as f:
        yaml.dump(repository_metadata, f)

def get_remotes():
    repository_metadata = load_repository_metadata()
    return repository_metadata["remotes"]

def gen_rsync_command(args):
    command = ["rsync", "-i", "-avzh"]
    if args.checksum:
        command.append("--checksum")
    return command

def push(args):
    check_init()
    remotes = get_remotes()
    print("[.] Trying to push to {} remotes.".format(len(remotes)))
    for remote in remotes:
        command = gen_rsync_command(args) + ['--dry-run', '.', remote["remote_path"]]
        print("[.] dry-run push to {}.".format(remote["name"]))
        print(command)
        subprocess.run(command, check=True)
        if input("Push to {}? [y/N] ".format(remote["name"])) != "y":
            continue
        
        command.remove('--dry-run')
        print("[.] push to {}.".format(remote["name"]))
        print(command)
        subprocess.run(command, check=True)

def pull(args):
    check_init()
    remotes = get_remotes()
    print("[.] Trying to pull from {} remotes.".format(len(remotes)))
    for remote in remotes:
        command = gen_rsync_command(args) + ['--dry-run', remote["remote_path"], '.']
        print("[.] dry-run pull from {}.".format(remote["name"]))
        print(command)
        subprocess.run(command, check=True)
        if input("Pull from {}? [y/N] ".format(remote["name"])) != "y":
            continue
        
        command.remove('--dry-run')
        print("[.] pull from {}.".format(remote["name"]))
        print(command)
        subprocess.run(command, check=True)

def remote_add(command, name, remote_path):
    check_init()
    print("[.] Trying to add remote {} at {}.".format(name, remote_path))

    repository_metadata = load_repository_metadata()
    remotes = repository_metadata["remotes"]
    for remote in remotes:
        if remote["name"] == name:
            raise SystemExit("[!] Remote {} already exists.".format(name))
        
    remotes.append({
        "name": name,
        "remote_path": remote_path,
    })

    save_repository_metadata(repository_metadata)
    print("[+] Added remote {} at {}.".format(name, remote_path))

def rm(args):
    check_init()
    raise NotImplementedError()

def mv(args):
    check_init()
    raise NotImplementedError()

def main():
    check_dependencies()

    """
    syncer init
    syncer push
    syncer pull
    syncer remote add <name> <0.0.0.0:/path/to/dir>
    syncer push --checksum
    syncer pull --checksum
    """
    argparser = argparse.ArgumentParser()
    subparsers = argparser.add_subparsers(dest="command")
    subparsers.required = True

    init_parser = subparsers.add_parser("init", help="Initialize a syncer repository.")
    init_parser.set_defaults(func=init)

    push_parser = subparsers.add_parser("push", help="Push changes to a remote.")
    push_parser.set_defaults(func=push)
    push_parser.add_argument("--checksum", action="store_true", help="Use checksums instead of timestamps to determine if a file has changed.")

    pull_parser = subparsers.add_parser("pull", help="Pull changes from a remote.")
    pull_parser.set_defaults(func=pull)
    pull_parser.add_argument("--checksum", action="store_true", help="Use checksums instead of timestamps to determine if a file has changed.")

    remote_parser = subparsers.add_parser("remote")
    remote_subparsers = remote_parser.add_subparsers(dest="remote_command")
    remote_subparsers.required = True
    
    remote_add_parser = remote_subparsers.add_parser("add")
    remote_add_parser.add_argument("name")
    remote_add_parser.add_argument("remote_path")
    remote_add_parser.set_defaults(func=lambda args: remote_add("add", args.name, args.remote_path))

    rm_parser = remote_subparsers.add_parser("rm")
    rm_parser.add_argument("path")
    rm_parser.set_defaults(func=rm)

    mv_parser = remote_subparsers.add_parser("mv")
    mv_parser.add_argument("src")
    mv_parser.add_argument("dst")
    mv_parser.set_defaults(func=mv)

    args = argparser.parse_args()
    args.func(args)

def check_dependencies():
    check_rsync()

if __name__ == "__main__":
    main()