class Huawei < Oxidized::Model
  using Refinements

  # Prompt regex - matches Huawei VRP prompts like <Huawei> or [Huawei]
  prompt /^.*(<[\w.-]+>)$/

  comment '# '

  # Hide sensitive information
  cmd :secret do |cfg|
    cfg.gsub! /(pin verify (?:auto|)).*/, '\1 <PIN hidden>'
    cfg.gsub! /(%\^%#.*%\^%#)/, '<secret hidden>'
    cfg
  end

  # Remove leading/trailing whitespace from output
  cmd :all do |cfg|
    cfg.cut_both
  end

  # Telnet login configuration
  cfg :telnet do
    username /^Username:$/
    password /^Password:$/
  end

  # SSH and Telnet post-login configuration
  cfg :telnet, :ssh do
    post_login 'screen-length 0 temporary'
    pre_logout 'quit'
  end

  # Display version - filter uptime lines and output as comment
  cmd 'display version' do |cfg|
    cfg = cfg.each_line.reject do |l|
      l.match(/uptime/) ||
        l.match(/^\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d(\.\d\d\d)? ?(\+\d\d:\d\d)?$/)
    end.join
    comment cfg
  end

  # Display device - filter timestamp lines and output as comment
  cmd 'display device' do |cfg|
    cfg = cfg.each_line.reject do |l|
      l.match(/^\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d(\.\d\d\d)? ?(\+\d\d:\d\d)?$/)
    end.join
    comment cfg
  end

  # Display current configuration - filter pagination and timestamp lines
  cmd 'display current-configuration' do |cfg|
    cfg = cfg.each_line.reject do |l|
      l.match(/---- More ----/) ||
        l.match(/^\[Pasted ~?\d+ lines?\]$/) ||
        l.match(/^\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d(\.\d\d\d)? ?(\+\d\d:\d\d)?$/)
    end.join
    cfg
  end
end
