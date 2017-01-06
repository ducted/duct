# TODO: Document
define duct::output($output, $config=false) {
  file {"/etc/duct/conf.d/output_${title}.yml":
    ensure  => present,
    content => template('duct/duct-output.yml.erb'),
    owner   => root,
    mode    => '0644',
    notify  => Service['duct'],
    require => File['/etc/duct/conf.d'],
  }
}
