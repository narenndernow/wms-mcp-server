
pipeline {
    agent any

    environment {
        IMAGE_NAME = 'nerender/wms-mcp-server'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }



       stage('Set Image Tag') {
    steps {
        script {
            def gitCommit = sh(
                script: 'git rev-parse --short=7 HEAD',
                returnStdout: true
            ).trim()

            env.IMAGE_TAG = gitCommit

            echo "IMAGE_TAG = ${env.IMAGE_TAG}"
        }
    }
}



stage('Build Docker Image') {
    steps {
        script {
            if (!env.IMAGE_TAG?.trim()) {
                error("IMAGE_TAG is empty!")
            }

            sh """
                docker build -t ${env.IMAGE_NAME}:${env.IMAGE_TAG} .
            """
        }
    }
}





        stage('Push to Docker Hub') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-credentials',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_TOKEN'
                    )
                ]) {
                    sh '''
                        echo "$DOCKER_TOKEN" | docker login \
                          -u "$DOCKER_USER" --password-stdin

                        docker push ${IMAGE_NAME}:${IMAGE_TAG}

                        docker logout
                    '''
                }
            }
        }
    }
}
