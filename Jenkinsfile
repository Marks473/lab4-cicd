pipeline {
    agent any

​    stages {
​        stage('Checkout') {
​            steps {
​                git branch: 'dev', url: 'https://github.com/Marks473/lab4-cicd.git'
​            }
​        }

​        stage('Build Docker Image') {
​            steps {
​                sh 'docker compose build'
​            }
​        }

​        stage('Run Tests') {
​            steps {
​                sh 'docker compose run --rm web python manage.py test'
​            }
​        }

​        stage('Start App') {
​            steps {
​                sh 'docker compose up -d'
​            }
​        }
​    }
}
 
