#!/usr/bin/env python2

# See: http://askubuntu.com/questions/345588/what-is-the-safest-way-to-clean-up-boot-partition#answer-430944

import re
import sys
import subprocess

'''Print and execute a system command'''
def call(command, stderr=True):
    print "$ %s\n" % command
    output = subprocess.check_output(command, stderr=subprocess.STDOUT if stderr else None, shell=True, universal_newlines=True)
    return output

# determine free space on boot
disk_space = call('df -k /boot')
matched = re.search('^\S+[\t ]+(\d+)\s+(?:\d+\s+){2}(\d+)%\s+(\/[\S]*)$', disk_space, re.M)

if not matched:
    raise SystemExit('Could not determine free space on /boot:\n\n%s' % disk_space)

# if /boot is its own partition, save ourselves some calculations
if matched.group(3) == '/boot':
    free_percent = int(matched.group(2))
# otherwise, determine /boot size as % of containing partition
else:
    part_size = matched.group(1)
    boot_space = call('du -ks /boot')
    matched = re.search('(\d+)\s+\/boot$', boot_space)
    free_percent = ( int(part_size) / int(matched.group(1)) ) / 100

# bail unless over X% full (75 by default)
min_percent = 75
if len(sys.argv) > 1:
    try:
        min_percent = int(sys.argv[1])
    except ValueError:
        pass

if free_percent < min_percent:
    raise SystemExit('Boot partition is only %s%% full' % free_percent)

# list all kernels
all_kernels = call('dpkg --list "linux-image*"')

# get running kernel
running_kernel = call('uname -r')

# de-dupe kernel versions by assigning as dict keys
remove_kernels = dict()
for line in all_kernels.split("\n"):
    # match only installed kernels
    matched = re.search('^ii\s+linux-image-([\d.]+-\d+-[a-z]+)', line)
    if matched:
        # skip running kernel
        if matched.group(1) not in running_kernel:
            remove_kernels[ matched.group(1) ] = True

# sort kernels to remove (as segmented versions)
remove_kernels = remove_kernels.keys()
remove_kernels.sort(key=lambda s: map(int, re.split('[.-]', re.split('-\D+$',s)[0])))

for version in remove_kernels:
    print 'Found: %s\n' % version

# if more than two, exclude the last two
if len(remove_kernels) > 2:
    del remove_kernels[-2:]

# remove all files for given versions on /boot
was_removed = False
for version in remove_kernels:
    # attempt to purge version
    try:
        call('dpkg --purge linux-image-%s' % version)
        call('dpkg --purge linux-headers-%s' % version)
    # fail gracefully if purge is not successful
    except subprocess.CalledProcessError as e:
        print 'Purge failed: %s' % e.output
    # otherwise note removal
    else:
        was_removed = True

# rebuild grub boot configurations
if was_removed:
    call('update-grub')
