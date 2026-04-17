class Huawei < Oxidized::Model
  prompt /^<.*>$/
  comment "# "

  cmd 'display current-configuration' do |cfg|
    lines = cfg.each_line.reject { |line| line =~ /---- More ----/ }.join
    lines
  end

  cfg :ssh do
    post_login "screen-length 0 temporary"
    pre_logout "quit"
  end
end