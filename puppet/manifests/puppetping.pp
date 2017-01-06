# TODO: Document
define duct::puppetping($service='ping', $route=false, $query='kernel="Linux"') {
  $orghosts = query_nodes($query)

  file { '/etc/duct/conf.d/puppet_pings.yml':
    ensure  => present,
    content => template('duct/puppet_pings.yml.erb'),
    owner   => root,
    mode    => '0644',
    notify  => Service['duct'],
    require => File['/etc/duct/conf.d'],
  }
}
