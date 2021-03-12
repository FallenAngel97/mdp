Vagrant.configure("2") do |config|

  config.ssh.username = 'vagrant'
  config.ssh.password = 'vagrant'
  config.ssh.insert_key = false
  config.vm.box = "ubuntu/trusty64"

  config.vm.define "192.168.33.10" do |web|
    web.vm.network "private_network", ip: "192.168.33.10"
  end

  config.vm.define "192.168.33.15" do |web2|
    web2.vm.network "private_network", ip: "192.168.33.15"
  end

end
