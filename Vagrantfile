# Simple Vagrant definition for Cider.

Vagrant::Config.run do |config|
    config.vm.box = 'ubuntu-12.04-i386'

    # The url from where the 'config.vm.box' box will be fetched if it doesn't
    # already exist on the user's system.
    config.vm.box_url = [
        'http://cloud-images.ubuntu.com',
        'vagrant/precise/current',
        'precise-server-cloudimg-i386-vagrant-disk1.box'
    ].join('/')

    # Give the VM two cores.
    config.vm.customize ['modifyvm', :id, '--cpus', 2]

    # This makes symlinks in the shared /vagrant folder work correctly on
    # VirtualBox. In general avoid symlinks in code as they do not work right
    # in Windows hosts.
    config.vm.customize [
        'setextradata',
        :id,
        'VBoxInternal2/SharedFoldersEnableSymlinksCreate/v-root',
        '1'
    ]

    # This causes VirtualBox to proxy DNS into the VM otherwise lookups will
    # fail.
    config.vm.customize ['modifyvm', :id, '--natdnshostresolver1', 'on']

    # RAM for the VM.
    config.vm.customize ['modifyvm', :id, '--memory', 2048]

    # List of ports to forward to the host.
    config.vm.forward_port 3333, 4444
end
