# deploy.sh - gvfs-mount FTP Webserver and rsync the website data
#
# This script contains some hard-coded variables and is configured specifically
# for Roll on Mouche's website!
# This script requires a file "../username.txt" containing the username for the
# FTP server.
#
# SYNOPSIS:
#   deploy.sh [OPTION...] [SRC]
#
# ARGUMENTS:
#   SRC
#       Source being passed to rsync. Default: ./ (content of current path)
#
# OPTIONS:
#   -n, --dry-run
#       Dry-run the rsync task to see what will be done.
#   -m, --keep-mounted
#       Do not unmount when the work is done.
#   -d, --dest
#       Custom destination path.

# -----------------------------------------------------------------------------
# argument checking ( https://stackoverflow.com/questions/192249/ )
# -----------------------------------------------------------------------------
POSITIONAL=()
while [[ $# -gt 0 ]]
do
    key="$1"

    case $key in
        -m|--keep-mounted)
        KEEPMOUNT=YES
        shift # past argument
        ;;
        -n|--dry-run)
        DRYRUN=YES
        shift # past argument
        ;;
        -d|--dest)
        DEST_PATH="$2"
        shift # past argument
        shift # past value
        ;;
        *)    # unknown option
        POSITIONAL+=("$1") # save it in an array for later
        shift # past argument
        ;;
    esac
done
set -- "${POSITIONAL[@]}" # restore positional parameters

[[ -n $1 ]] && SRC_PATH=$1 || SRC_PATH="./"

DRY="--dry-run"
[ -z $DRYRUN ] && DRY=""

# -----------------------------------------------------------------------------
# the hardcoded parameters
# -----------------------------------------------------------------------------
FTPSERVER=`cat ../servername.txt`  # make sure not to have a trailing "/"
FTPUSER=`cat ../username.txt`
DEST_PATH_SERVER="/run/user/1000/gvfs/ftp:host=$FTPSERVER,user=$FTPUSER/web"
TMP_DIR="$SRC_PATH.rsync_tmp"
SERVER_URL="ftp://$FTPUSER@$FTPSERVER"

# -----------------------------------------------------------------------------
# the actaual tasks
# -----------------------------------------------------------------------------
[ ! -d $TMP_DIR ] && echo "Create tmp dir $TMP_DIR …" && mkdir $TMP_DIR

if [ -z $DEST_PATH ]; then
    DEST_PATH=$DEST_PATH_SERVER
    DO_MOUNT=true
fi

if [ "$DO_MOUNT" = true ]; then
    echo "Mount FTP server …"
    gvfs-mount $SERVER_URL
fi

echo "Start sync …"
rsync \
    --recursive \
    --update \
    --delete \
    --exclude .git \
    --exclude error \
    --exclude stats \
    --exclude todo.txt \
    --exclude deploy.sh \
    --temp-dir=$TMP_DIR \
    $DRY \
    --verbose \
    --progress \
    --stats \
    $SRC_PATH \
    $DEST_PATH

if [ "$DO_MOUNT" = true ]; then
    if [ -z $KEEPMOUNT ]; then
        echo "Unmount FTP server …"
        gvfs-mount -u $SERVER_URL
        echo "Done."
    else
        echo "Done."
        echo "Server still mounted. Unmount with"
        echo "gvfs-mount -u $SERVER_URL"
    fi
else
    echo "Done."
fi
