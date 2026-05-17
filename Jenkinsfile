pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
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

        stage('Start App') {
            steps {
                sh 'docker compose up -d'
            }
        }
        
        stage('Smoke Test') {
	    steps {
		sh 'sleep 5'
		sh 'curl -f http://localhost:8000/'
	    }
	}
    }
}
