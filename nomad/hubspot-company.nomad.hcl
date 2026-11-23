job "hubspot-company" {
  datacenters = ["dc1"]
  type        = "service"

  group "hubspot-company" {
    count = 1

    network {
      port "http" {
        static = 5104
        to     = 5104
      }
    }

    service {
      name     = "hubspot-company"
      provider = "consul"
      port     = "http"

      check {
        name     = "hubspot-company-health"
        type     = "http"
        path     = "/scan/health"
        interval = "10s"
        timeout  = "2s"
      }
    }

    task "web" {
      driver = "docker"

      config {
        image      = "hubspot-company:staging"
        ports      = ["http"]
        force_pull = false
      }

      env {
        FLASK_ENV   = "staging"
        DATABASE_URL = "postgresql://user:change_me@host.docker.internal:5432/hubspot_db"
      }

      resources {
        cpu    = 500
        memory = 768
      }
    }
  }
}
