# TODO: Document
define duct::source($source, $interval='60.0', $config=false,
  $critical=false, $warning=false, $service_name=false, $tags=false
  ) {
  $service = $title

  file {"/etc/duct/conf.d/${service}.yml":
    ensure  => present,
    content => template('duct/duct-source.yml.erb'),
    notify  => Service['duct'],
    require => File['/etc/duct/conf.d'],
  }
}
