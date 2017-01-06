# TODO: Document
class duct(
    $interval=1.0,
    $default_ttl=60.0,
    $outputs={},
    $sources={}
  ) {

  if $::operatingsystem == 'Ubuntu' {
    apt::source {'duct':
      location   => 'https://calston.github.io/duct/ubuntu',
      repos      => 'main',
      key        => 'B70AAA23106FEDF92AD79F3D6FC4C33F2B2A5480',
      key_server => 'keyserver.ubuntu.com'
    }
  }
  if $::operatingsystem == 'Debian' {
    apt::source {'duct':
      location   => 'https://calston.github.io/duct/debian',
      repos      => 'main',
      key        => 'B70AAA23106FEDF92AD79F3D6FC4C33F2B2A5480',
      key_server => 'keyserver.ubuntu.com'
    }
  }

  package{'duct':
    ensure  => latest,
    require => Apt::Source['duct']
  }

  service{'duct':
    ensure  => running,
    require => Package['duct']
  }

  file{'/etc/duct/conf.d':
    ensure  => directory,
    require => Package['duct']
  }

  file{'/etc/duct/duct.yml':
    ensure  => present,
    content => template('duct/duct.yml.erb'),
    notify  => Service['duct'],
    require => File['/etc/duct/conf.d'],
  }

  create_resources(duct::output, $outputs)

  create_resources(duct::source, $sources)
}

