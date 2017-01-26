# -*- mode: ruby -*-
# vi: set ft=ruby :

$fucking_locale = <<SCRIPT
    locale-gen en_US en_US.UTF-8 pt_BR.UTF-8 de_DE.UTF-8
    dpkg-reconfigure locales
SCRIPT

$dependencies = <<SCRIPT
    DEBIAN_FRONTEND=noninteractive apt-get update
    # pyenv
    DEBIAN_FRONTEND=noninteractive apt-get install -y curl python-dev \
        libreadline-dev libbz2-dev libssl-dev libsqlite3-dev libxslt1-dev \
        libxml2-dev libxslt1-dev git python-pip build-essential automake libtool libffi-dev libgmp-dev pkg-config
SCRIPT

$pyenv = <<SCRIPT
if [ ! -d ~/.pyenv ]; then
    pip install --egg pyenv
else
    . ~/.bash_profile
    pyenv update
fi
if [ ! -f ~/.bash_profile ]; then
    touch ~/.bash_profile
fi
if ! grep -q pyenv ~/.bash_profile; then
    echo '
# pyenv
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
export PYENV_VIRTUALENVWRAPPER_PREFER_PYVENV="true"
' >> ~/.bash_profile
fi

. ~/.bash_profile
pyenv install 2.7.9
pyenv rehash
pyenv global 2.7.9
SCRIPT

$requirements = <<SCRIPT
pip install --upgrade pip
pip install -r /vagrant/requirements.txt
SCRIPT

$node_dependencies = <<SCRIPT
    curl -sL https://deb.nodesource.com/setup_6.x | sudo -E bash -
    apt-get install -y nodejs
    cd /vagrant/
    npm install --save gnosisjs 
SCRIPT

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure("2") do |config|
  # The most common configuration options are documented and commented below.
  # For a complete reference, please see the online documentation at
  # https://docs.vagrantup.com.

  # Every Vagrant development environment requires a box. You can search for
  # boxes at https://atlas.hashicorp.com/search.
  config.vm.box = "ubuntu/trusty64"
  config.vm.provider "virtualbox" do |v|
      v.memory = 3072
      v.cpus = 2
  end

  config.ssh.forward_agent = true
  config.vm.network :forwarded_port, host: 8545, guest: 8545

  # Disable automatic box update checking. If you disable this, then
  # boxes will only be checked for updates when the user runs
  # `vagrant box outdated`. This is not recommended.
  # config.vm.box_check_update = false

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine. In the example below,
  # accessing "localhost:8080" will access port 80 on the guest machine.
  # config.vm.network "forwarded_port", guest: 80, host: 8080

  # Create a private network, which allows host-only access to the machine
  # using a specific IP.
  # config.vm.network "private_network", ip: "192.168.33.10"

  # Create a public network, which generally matched to bridged network.
  # Bridged networks make the machine appear as another physical device on
  # your network.
  # config.vm.network "public_network"

  # Share an additional folder to the guest VM. The first argument is
  # the path on the host to the actual folder. The second argument is
  # the path on the guest to mount the folder. And the optional third
  # argument is a set of non-required options.
  # config.vm.synced_folder "../data", "/vagrant_data"

  # Provider-specific configuration so you can fine-tune various
  # backing providers for Vagrant. These expose provider-specific options.
  # Example for VirtualBox:
  #
  # config.vm.provider "virtualbox" do |vb|
  #   # Display the VirtualBox GUI when booting the machine
  #   vb.gui = true
  #
  #   # Customize the amount of memory on the VM:
  #   vb.memory = "1024"
  # end
  #
  # View the documentation for the provider you are using for more
  # information on available options.

  # Define a Vagrant Push strategy for pushing to Atlas. Other push strategies
  # such as FTP and Heroku are also available. See the documentation at
  # https://docs.vagrantup.com/v2/push/atlas.html for more information.
  # config.push.define "atlas" do |push|
  #   push.app = "YOUR_ATLAS_USERNAME/YOUR_APPLICATION_NAME"
  # end

  # Enable provisioning with a shell script. Additional provisioners such as
  # Puppet, Chef, Ansible, Salt, and Docker are also available. Please see the
  # documentation for more information about their specific syntax and use.
  # config.vm.provision "shell", inline: <<-SHELL
  #   apt-get update
  #   apt-get install -y apache2
  # SHELL

  config.vm.provision "shell", inline: $dependencies
  config.vm.provision "shell", inline: $fucking_locale
  config.vm.provision "shell", inline: $pyenv, privileged: false
  config.vm.provision "shell", inline: $requirements, privileged: false
  config.vm.provision "shell", inline: $node_dependencies, privileged: true
end
