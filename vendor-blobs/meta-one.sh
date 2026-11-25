#!/bin/bash
# One line of metadata per path in the stock vendor.img as stored in the image.
# usage: scan-one.sh <image> <abs path>  -> TSV: path,type,size,ondisk,nid,links,uid,gid,mode,xattr
img=$1; p=$2
out=$(dump.erofs --path="$p" "$img" 2>/dev/null | tr '\n' '|')
type=$(grep -oE '\b(regular file|directory|symlink file|symbolic link|character device|block device|fifo|socket)\b' <<<"$out" | head -1)
size=$(grep -oE 'Size: *[0-9]+' <<<"$out" | head -1 | grep -oE '[0-9]+')
ondisk=$(grep -oE 'On-disk size: *[0-9]+' <<<"$out" | head -1 | grep -oE '[0-9]+')
nid=$(grep -oE 'NID: *[0-9]+' <<<"$out" | head -1 | grep -oE '[0-9]+')
links=$(grep -oE 'Links: *[0-9]+' <<<"$out" | head -1 | grep -oE '[0-9]+')
ids=$(grep -oE 'Uid: *[0-9]+ +Gid: *[0-9]+' <<<"$out" | head -1)
uid=$(grep -oE 'Uid: *[0-9]+' <<<"$ids" | grep -oE '[0-9]+')
gid=$(grep -oE 'Gid: *[0-9]+' <<<"$ids" | grep -oE '[0-9]+')
mode=$(grep -oE 'Access: *[0-7]+' <<<"$out" | head -1 | grep -oE '[0-7]+')
xattr=$(grep -oE 'Xattr size: *[0-9]+' <<<"$out" | head -1 | grep -oE '[0-9]+')
printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$p" "${type:-unknown}" "${size:-}" "${ondisk:-}" "${nid:-}" "${links:-}" "${uid:-}" "${gid:-}" "${mode:-}" "${xattr:-0}"
