ES_NODES_STATS = {
  "_nodes" : {
    "total" : 1,
    "successful" : 1,
    "failed" : 0
  },
  "cluster_name" : "elasticsearch",
  "nodes" : {
    "EqQZrW8CQ7SFAuIdMrQWcA" : {
      "timestamp" : 1486378925372,
      "name" : "EqQZrW8",
      "transport_address" : "172.17.0.2:9300",
      "host" : "172.17.0.2",
      "ip" : "172.17.0.2:9300",
      "roles" : [
        "master",
        "data",
        "ingest"
      ],
      "indices" : {
        "docs" : {
          "count" : 857519,
          "deleted" : 2
        },
        "store" : {
          "size_in_bytes" : 204886278,
          "throttle_time_in_millis" : 0
        },
        "indexing" : {
          "index_total" : 0,
          "index_time_in_millis" : 0,
          "index_current" : 0,
          "index_failed" : 0,
          "delete_total" : 0,
          "delete_time_in_millis" : 0,
          "delete_current" : 0,
          "noop_update_total" : 0,
          "is_throttled" : False,
          "throttle_time_in_millis" : 0
        },
        "get" : {
          "total" : 0,
          "time_in_millis" : 0,
          "exists_total" : 0,
          "exists_time_in_millis" : 0,
          "missing_total" : 0,
          "missing_time_in_millis" : 0,
          "current" : 0
        },
        "search" : {
          "open_contexts" : 0,
          "query_total" : 0,
          "query_time_in_millis" : 0,
          "query_current" : 0,
          "fetch_total" : 0,
          "fetch_time_in_millis" : 0,
          "fetch_current" : 0,
          "scroll_total" : 0,
          "scroll_time_in_millis" : 0,
          "scroll_current" : 0,
          "suggest_total" : 0,
          "suggest_time_in_millis" : 0,
          "suggest_current" : 0
        },
        "merges" : {
          "current" : 0,
          "current_docs" : 0,
          "current_size_in_bytes" : 0,
          "total" : 0,
          "total_time_in_millis" : 0,
          "total_docs" : 0,
          "total_size_in_bytes" : 0,
          "total_stopped_time_in_millis" : 0,
          "total_throttled_time_in_millis" : 0,
          "total_auto_throttle_in_bytes" : 650117120
        },
        "refresh" : {
          "total" : 31,
          "total_time_in_millis" : 114
        },
        "flush" : {
          "total" : 31,
          "total_time_in_millis" : 2
        },
        "warmer" : {
          "current" : 0,
          "total" : 62,
          "total_time_in_millis" : 80
        },
        "query_cache" : {
          "memory_size_in_bytes" : 0,
          "total_count" : 0,
          "hit_count" : 0,
          "miss_count" : 0,
          "cache_size" : 0,
          "cache_count" : 0,
          "evictions" : 0
        },
        "fielddata" : {
          "memory_size_in_bytes" : 0,
          "evictions" : 0
        },
        "completion" : {
          "size_in_bytes" : 0
        },
        "segments" : {
          "count" : 135,
          "memory_in_bytes" : 1633192,
          "terms_memory_in_bytes" : 1259900,
          "stored_fields_memory_in_bytes" : 97984,
          "term_vectors_memory_in_bytes" : 0,
          "norms_memory_in_bytes" : 22464,
          "points_memory_in_bytes" : 67576,
          "doc_values_memory_in_bytes" : 185268,
          "index_writer_memory_in_bytes" : 0,
          "version_map_memory_in_bytes" : 0,
          "fixed_bit_set_memory_in_bytes" : 0,
          "max_unsafe_auto_id_timestamp" : -1,
          "file_sizes" : { }
        },
        "translog" : {
          "operations" : 0,
          "size_in_bytes" : 2666
        },
        "request_cache" : {
          "memory_size_in_bytes" : 0,
          "evictions" : 0,
          "hit_count" : 0,
          "miss_count" : 0
        },
        "recovery" : {
          "current_as_source" : 0,
          "current_as_target" : 0,
          "throttle_time_in_millis" : 0
        }
      },
      "os" : {
        "timestamp" : 1486378925400,
        "cpu" : {
          "percent" : 2,
          "load_average" : {
            "1m" : 0.07,
            "5m" : 0.17,
            "15m" : 0.16
          }
        },
        "mem" : {
          "total_in_bytes" : 8242167808,
          "free_in_bytes" : 1547399168,
          "used_in_bytes" : 6694768640,
          "free_percent" : 19,
          "used_percent" : 81
        },
        "swap" : {
          "total_in_bytes" : 0,
          "free_in_bytes" : 0,
          "used_in_bytes" : 0
        }
      },
      "process" : {
        "timestamp" : 1486378925400,
        "open_file_descriptors" : 263,
        "max_file_descriptors" : 1048576,
        "cpu" : {
          "percent" : 0,
          "total_in_millis" : 29610
        },
        "mem" : {
          "total_virtual_in_bytes" : 6208012288
        }
      },
      "jvm" : {
        "timestamp" : 1486378925400,
        "uptime_in_millis" : 529762,
        "mem" : {
          "heap_used_in_bytes" : 333092040,
          "heap_used_percent" : 15,
          "heap_committed_in_bytes" : 2112618496,
          "heap_max_in_bytes" : 2112618496,
          "non_heap_used_in_bytes" : 72575848,
          "non_heap_committed_in_bytes" : 77107200,
          "pools" : {
            "young" : {
              "used_in_bytes" : 221542480,
              "max_in_bytes" : 279183360,
              "peak_used_in_bytes" : 279183360,
              "peak_max_in_bytes" : 279183360
            },
            "survivor" : {
              "used_in_bytes" : 34865136,
              "max_in_bytes" : 34865152,
              "peak_used_in_bytes" : 34865152,
              "peak_max_in_bytes" : 34865152
            },
            "old" : {
              "used_in_bytes" : 76684424,
              "max_in_bytes" : 1798569984,
              "peak_used_in_bytes" : 76684424,
              "peak_max_in_bytes" : 1798569984
            }
          }
        },
        "threads" : {
          "count" : 41,
          "peak_count" : 51
        },
        "gc" : {
          "collectors" : {
            "young" : {
              "collection_count" : 3,
              "collection_time_in_millis" : 161
            },
            "old" : {
              "collection_count" : 1,
              "collection_time_in_millis" : 89
            }
          }
        },
        "buffer_pools" : {
          "direct" : {
            "count" : 41,
            "used_in_bytes" : 140615436,
            "total_capacity_in_bytes" : 140615435
          },
          "mapped" : {
            "count" : 294,
            "used_in_bytes" : 203794442,
            "total_capacity_in_bytes" : 203794442
          }
        },
        "classes" : {
          "current_loaded_count" : 9947,
          "total_loaded_count" : 9947,
          "total_unloaded_count" : 0
        }
      },
      "thread_pool" : {
        "bulk" : {
          "threads" : 0,
          "queue" : 0,
          "active" : 0,
          "rejected" : 0,
          "largest" : 0,
          "completed" : 0
        },
        "fetch_shard_started" : {
          "threads" : 1,
          "queue" : 0,
          "active" : 0,
          "rejected" : 0,
          "largest" : 8,
          "completed" : 31
        },
        "fetch_shard_store" : {
          "threads" : 0,
          "queue" : 0,
          "active" : 0,
          "rejected" : 0,
          "largest" : 0,
          "completed" : 0
        },
        "flush" : {
          "threads" : 2,
          "queue" : 0,
          "active" : 0,
          "rejected" : 0,
          "largest" : 2,
          "completed" : 62
        },
        "force_merge" : {
          "threads" : 0,
          "queue" : 0,
          "active" : 0,
          "rejected" : 0,
          "largest" : 0,
          "completed" : 0
        },
        "generic" : {
          "threads" : 4,
          "queue" : 0,
          "active" : 0,
          "rejected" : 0,
          "largest" : 4,
          "completed" : 94
        },
        "get" : {
          "threads" : 0,
          "queue" : 0,
          "active" : 0,
          "rejected" : 0,
          "largest" : 0,
          "completed" : 0
        },
        "index" : {
          "threads" : 0,
          "queue" : 0,
          "active" : 0,
          "rejected" : 0,
          "largest" : 0,
          "completed" : 0
        },
        "listener" : {
          "threads" : 0,
          "queue" : 0,
          "active" : 0,
          "rejected" : 0,
          "largest" : 0,
          "completed" : 0
        },
        "management" : {
          "threads" : 2,
          "queue" : 0,
          "active" : 1,
          "rejected" : 0,
          "largest" : 2,
          "completed" : 74
        },
        "refresh" : {
          "threads" : 2,
          "queue" : 0,
          "active" : 0,
          "rejected" : 0,
          "largest" : 2,
          "completed" : 2380
        },
        "search" : {
          "threads" : 0,
          "queue" : 0,
          "active" : 0,
          "rejected" : 0,
          "largest" : 0,
          "completed" : 0
        },
        "snapshot" : {
          "threads" : 0,
          "queue" : 0,
          "active" : 0,
          "rejected" : 0,
          "largest" : 0,
          "completed" : 0
        },
        "warmer" : {
          "threads" : 1,
          "queue" : 0,
          "active" : 0,
          "rejected" : 0,
          "largest" : 2,
          "completed" : 62
        }
      },
      "fs" : {
        "timestamp" : 1486378925401,
        "total" : {
          "total_in_bytes" : 125891006464,
          "free_in_bytes" : 58239213568,
          "available_in_bytes" : 51820724224,
          "spins" : "true"
        },
        "data" : [
          {
            "path" : "/usr/share/elasticsearch/data/nodes/0",
            "mount" : "/usr/share/elasticsearch/data (/dev/sda1)",
            "type" : "ext4",
            "total_in_bytes" : 125891006464,
            "free_in_bytes" : 58239213568,
            "available_in_bytes" : 51820724224,
            "spins" : "true"
          }
        ],
        "io_stats" : {
          "devices" : [
            {
              "device_name" : "sda1",
              "operations" : 5771,
              "read_operations" : 1380,
              "write_operations" : 4391,
              "read_kilobytes" : 49116,
              "write_kilobytes" : 132892
            }
          ],
          "total" : {
            "operations" : 5771,
            "read_operations" : 1380,
            "write_operations" : 4391,
            "read_kilobytes" : 49116,
            "write_kilobytes" : 132892
          }
        }
      },
      "transport" : {
        "server_open" : 0,
        "rx_count" : 16,
        "rx_size_in_bytes" : 7056,
        "tx_count" : 16,
        "tx_size_in_bytes" : 7056
      },
      "http" : {
        "current_open" : 1,
        "total_opened" : 8
      },
      "breakers" : {
        "request" : {
          "limit_size_in_bytes" : 1267571097,
          "limit_size" : "1.1gb",
          "estimated_size_in_bytes" : 0,
          "estimated_size" : "0b",
          "overhead" : 1.0,
          "tripped" : 0
        },
        "fielddata" : {
          "limit_size_in_bytes" : 1267571097,
          "limit_size" : "1.1gb",
          "estimated_size_in_bytes" : 0,
          "estimated_size" : "0b",
          "overhead" : 1.03,
          "tripped" : 0
        },
        "in_flight_requests" : {
          "limit_size_in_bytes" : 2112618496,
          "limit_size" : "1.9gb",
          "estimated_size_in_bytes" : 0,
          "estimated_size" : "0b",
          "overhead" : 1.0,
          "tripped" : 0
        },
        "parent" : {
          "limit_size_in_bytes" : 1478832947,
          "limit_size" : "1.3gb",
          "estimated_size_in_bytes" : 0,
          "estimated_size" : "0b",
          "overhead" : 1.0,
          "tripped" : 0
        }
      },
      "script" : {
        "compilations" : 0,
        "cache_evictions" : 0
      },
      "discovery" : {
        "cluster_state_queue" : {
          "total" : 0,
          "pending" : 0,
          "committed" : 0
        }
      },
      "ingest" : {
        "total" : {
          "count" : 0,
          "time_in_millis" : 0,
          "current" : 0,
          "failed" : 0
        },
        "pipelines" : { }
      }
    }
  }
}

ES_CLUSTER_STATS = {
  "_nodes" : {
    "total" : 1,
    "successful" : 1,
    "failed" : 0
  },
  "cluster_name" : "elasticsearch",
  "timestamp" : 1486378969751,
  "status" : "yellow",
  "indices" : {
    "count" : 7,
    "shards" : {
      "total" : 31,
      "primaries" : 31,
      "replication" : 0.0,
      "index" : {
        "shards" : {
          "min" : 1,
          "max" : 5,
          "avg" : 4.428571428571429
        },
        "primaries" : {
          "min" : 1,
          "max" : 5,
          "avg" : 4.428571428571429
        },
        "replication" : {
          "min" : 0.0,
          "max" : 0.0,
          "avg" : 0.0
        }
      }
    },
    "docs" : {
      "count" : 857519,
      "deleted" : 2
    },
    "store" : {
      "size_in_bytes" : 204886278,
      "throttle_time_in_millis" : 0
    },
    "fielddata" : {
      "memory_size_in_bytes" : 0,
      "evictions" : 0
    },
    "query_cache" : {
      "memory_size_in_bytes" : 0,
      "total_count" : 0,
      "hit_count" : 0,
      "miss_count" : 0,
      "cache_size" : 0,
      "cache_count" : 0,
      "evictions" : 0
    },
    "completion" : {
      "size_in_bytes" : 0
    },
    "segments" : {
      "count" : 135,
      "memory_in_bytes" : 1633192,
      "terms_memory_in_bytes" : 1259900,
      "stored_fields_memory_in_bytes" : 97984,
      "term_vectors_memory_in_bytes" : 0,
      "norms_memory_in_bytes" : 22464,
      "points_memory_in_bytes" : 67576,
      "doc_values_memory_in_bytes" : 185268,
      "index_writer_memory_in_bytes" : 0,
      "version_map_memory_in_bytes" : 0,
      "fixed_bit_set_memory_in_bytes" : 0,
      "max_unsafe_auto_id_timestamp" : -1,
      "file_sizes" : { }
    }
  },
  "nodes" : {
    "count" : {
      "total" : 1,
      "data" : 1,
      "coordinating_only" : 0,
      "master" : 1,
      "ingest" : 1
    },
    "versions" : [
      "5.0.2"
    ],
    "os" : {
      "available_processors" : 4,
      "allocated_processors" : 4,
      "names" : [
        {
          "name" : "Linux",
          "count" : 1
        }
      ],
      "mem" : {
        "total_in_bytes" : 8242167808,
        "free_in_bytes" : 1550000128,
        "used_in_bytes" : 6692167680,
        "free_percent" : 19,
        "used_percent" : 81
      }
    },
    "process" : {
      "cpu" : {
        "percent" : 0
      },
      "open_file_descriptors" : {
        "min" : 263,
        "max" : 263,
        "avg" : 263
      }
    },
    "jvm" : {
      "max_uptime_in_millis" : 574083,
      "versions" : [
        {
          "version" : "1.8.0_111",
          "vm_name" : "OpenJDK 64-Bit Server VM",
          "vm_version" : "25.111-b14",
          "vm_vendor" : "Oracle Corporation",
          "count" : 1
        }
      ],
      "mem" : {
        "heap_used_in_bytes" : 335531024,
        "heap_max_in_bytes" : 2112618496
      },
      "threads" : 41
    },
    "fs" : {
      "total_in_bytes" : 125891006464,
      "free_in_bytes" : 58239176704,
      "available_in_bytes" : 51820687360,
      "spins" : "true"
    },
    "plugins" : [ ],
    "network_types" : {
      "transport_types" : {
        "netty4" : 1
      },
      "http_types" : {
        "netty4" : 1
      }
    }
  }
}

APACHE_STATS = """Total Accesses: 46
Total kBytes: 39
CPULoad: .036
Uptime: 4564
ReqPerSec: .5
BytesPerSec: 8.75
BytesPerReq: 868.125
BusyWorkers: 2
IdleWorkers: 48
ConnsTotal: 9
ConnsAsyncWriting: 2
ConnsAsyncKeepAlive: 3
ConnsAsyncClosing: 4
Scoreboard: _________________________________________________W...................................................................................................."""

SFLOW_PACKET = b'\x00\x00\x00\x05\x00\x00\x00\x01\xac\x1e\x00\x05\x00\x00\x00\x00\x00\x00\x02L\x01?lD\x00\x00\x00\x05\x00\x00\x00\x01\x00\x00\x00\xc4\x00\x00\x01\xff\x00\x00\x00\x10\x00\x00\x00\x80\x00(\x1d6\x00\x00\x03\x9a\x00\x00\x00\x03\x00\x00\x00\x10\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x84\x00\x00\x00\x01\x00\x00\x00u\x00\x00\x00\x04\x00\x00\x00t\xe4\xce\x8f.\x8a\xd4\xd4\xcam\x97r*\x08\x00Ex\x00cM-\x00\x007\x11kh)\x86\xf4\x89\xac\x1e\x00O\x05\xd8\xe3\xeb\x00O\xe3\x9d\xd8\xd0m\x15B\x81;\xda\x98\xa7\xd0\x00\t\xc7\xbe>K\x9b\xd5\xd3n\x15\xb9U\x1c0\x1e]+i2\xc9\xb5N4\xca"G\x1f\xfe\x86H\x9b\xc0\xa0\xb9\x9d\x97\xb9yHMIzI\xf9\xc8\xcd\x88\xadgtx\x85\x90\xf1\xfa_\x98-\x1a\x00\x00\x00\x00\x00\x03\xe9\x00\x00\x00\x10\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x94\x00\x00\x01\xd4\x00\x00\x00\n\x00\x00\x00\x80\x00fH)\x00\x00\x04\x0b\x00\x00\x00\x03\x00\x00\x00\n\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00T\x00\x00\x00\x01\x00\x00\x00F\x00\x00\x00\x04\x00\x00\x00D(77\x1b\x02\xf4\xd4\xcam\x97r*\x08\x00E\x80\x004\xb6\x13@\x00&\x06\xdf\xa22\x11\xe0\x11\xac\x1e\x00M\x01\xbb\xee\xae\x953w\x93"j\xbb\x1d\x80\x10\x00S\x0f\xb6\x00\x00\x01\x01\x08\n\x83\xe4\x92\x18ASv\x1d\x00\x00\x00\x00\x03\xe9\x00\x00\x00\x10\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x94\x00\x00\x01\xd5\x00\x00\x00\n\x00\x00\x00\x80\x00fH)\x00\x00\x04\x10\x00\x00\x00\n\x00\x00\x00\x03\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00T\x00\x00\x00\x01\x00\x00\x00F\x00\x00\x00\x04\x00\x00\x00D\xd4\xcam\x97r*(\xcf\xe9Z\xd8a\x08\x00E\x00\x004\x13\x89@\x00@\x06~8\xac\x1e\x00ZRK\xaa?\xf1\xfe\xed\xe1"\xe8\x97\xd6c\xbfC\x0e\x80\x11 \x00N\x9c\x00\x00\x01\x01\x08\n;\x829Y\x00\x11\xa8\xc3\x00\x00\x00\x00\x03\xe9\x00\x00\x00\x10\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\xff\xff\xff\xff\x00\x00\x00\x02\x00\x00\x00\xa8\x00\x00\x00!\x00\x00\x00\x0c\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00X\x00\x00\x00\x0c\x00\x00\x00\x06\x00\x00\x00\x00\x00\x98\x96\x80\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x004\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x94\x00\x00\x02\x00\x00\x00\x00\x10\x00\x00\x00\x80\x00(\x1e\x1a\x00\x00\x03\x9b\x00\x00\x00\x10\x00\x00\x00\x03\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00T\x00\x00\x00\x01\x00\x00\x00F\x00\x00\x00\x04\x00\x00\x00D\xd4\xcam\x97r*\\\n[\xe0\xe4\x14\x08\x00E\x00\x004\x04\r@\x00@\x06\x11\xfa\xac\x1e\x00\xae\x17C`\xae\x8f\xe0\x01\xbb\xac ;\xa8\x10\xc0\xab\xd7\x80\x10/\xea\x0e\'\x00\x00\x01\x01\x08\n\x00JuM\xe0\xd3\x87\x87\x00\x00\x00\x00\x03\xe9\x00\x00\x00\x10\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\xff\xff\xff\xff'

CONFIG_TEST = """outputs:
    - output: duct.outputs.logger.Logger
interval: 1.0
ssh_username: colin
include_path: testdir
mergehash:
    test:
        foo: bar
    test2:
        bar: baz
sources:
    - service: memory
      source: duct.sources.linux.basic.Memory
      interval: 10.0"""

CONFIG_INCLUDE ="""toolbox:
  standard:
    defaults:
      use_ssh: True
      interval: 1
    sources:
      - service: memory
        source: duct.sources.linux.basic.Memory
      - service: cpu
        source: duct.sources.linux.basic.CPU
blueprint:
  - toolbox: standard
    defaults:
      interval: 2
    sets:
      hostname:
        - test1
        - test2
        - test3
      use_ssh:
        - True
        - False
mergehash:
    test:
        bar: baz
    test3:
        foo: bar
sources:
    - service: memory
      source: duct.sources.linux.basic.Memory
      interval: 5.0\n"""
