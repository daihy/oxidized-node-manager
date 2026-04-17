require "tempfile"
require "pty"

require "oxidized/input/ssh"

class Oxidized::Huaweissh < Oxidized::SSH
  def connect(node)
    @node = node
    @host = @node.ip
    @user = @node.auth[:username]
    @pass = @node.auth[:password]
    @port = vars(:ssh_port) || 32410

    password = @pass

    script = <<~SCRIPT
      set timeout 120
      log_user 1
      spawn ssh -o StrictHostKeyChecking=no -o KexAlgorithms=diffie-hellman-group-exchange-sha1 -o PubkeyAuthentication=no -o PreferredAuthentications=password -o ConnectTimeout=30 -p #{@port} #{@user}@#{@host}
      expect "assword:" { send "#{password}\\r" }
      expect -re {<.*>}
      send "screen-length 0 temporary\\r"
      expect -re {<.*>}
      send "display current-configuration\\r"
      while {1} { expect { -re {<.*>} { break } -re {---- More ----} { send " " } timeout { break } } }
      send "quit\\r"
      expect eof
    SCRIPT

    script_file = Tempfile.new(["huawei", ".exp"])
    script_file.write(script)
    script_file.chmod(0755)
    script_file.close

    @log = File.open(File.join(Oxidized::Config::LOG, "#{@host}-huawei"), "w")
    @log.sync = true

    @pty = PTY.spawn("expect #{script_file.path}")
    @input = @pty[0]
    @output = @pty[1]
    @pid = @pty[2]

    wait_discovery
    script_file.unlink
  rescue => e
    script_file.unlink if script_file
    raise
  end
end