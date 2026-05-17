pipeline {
    agent any

    stages {
        stage('Cleanup') {
            steps {
                sh 'docker compose down -v || true'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker compose build'
            }
        }

        stage('Run Tests') {
            steps {
                sh 'docker compose run --rm web python manage.py test'
            }
        }

        stage('Apply Migrations') {
            steps {
                sh 'docker compose run --rm web python manage.py migrate'
            }
        }

        stage('Start App') {
            steps {
                sh 'docker compose up -d'
            }
        }

        stage('Smoke Test') {
            steps {
                sh '''
                    for i in $(seq 1 10); do
                      code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/ || true)
                      echo "HTTP status: $code"
                      if [ "$code" = "200" ]; then
                        exit 0
                      fi
                      sleep 3
                    done
                    exit 1
                '''
            }
        }
    }

    post {
        always {
            sh 'docker compose logs web || true'
        }
    }
}
