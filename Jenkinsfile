pipeline {
    agent any
    options {
        skipStagesAfterUnstable()
    }
    stages {        
        stage('Build') { 
            steps { 
                script {
                    app = docker.build("backend")
                }
            }
        }
        stage('Logging into AWS ECR') {
            steps {
                script {
                    sh """
                        aws ecr get-login-password --region us-east-1 | \
                        docker login --username AWS --password-stdin ${BACKEND_ECR_LINK}
                    """
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    docker.withRegistry("https://${BACKEND_ECR_LINK}") {
                        app.push("${env.BUILD_NUMBER}")
                    }
                }
            }
        }

        stage('Update ArgoCD values') {
            steps {
                sshagent(['github_ssh_key']) {
                    script {
                        def GIT_REPO = "git@github.com:Core5-team/illuminati_gitops.git"
                        def FILE_PATH = "envs/prod/backend-values.yaml"
                        def BRANCH = "main"

                        sh """
                            rm -rf gitops-repo
                            git clone ${GIT_REPO} gitops-repo
                            cd gitops-repo
                            git checkout ${BRANCH}

                            sed -i "s/^buildVersion: \".*\"/buildVersion: \"${BUILD_NUMBER}\"/" ${FILE_PATH}


                            git config user.email "jenkins@ci"
                            git config user.name "Jenkins Bot"

                            git add ${FILE_PATH}
                            git commit -m "Update buildVersion to ${env.BUILD_NUMBER}"
                            git push origin ${BRANCH}
                        """
                    }
                }
            }
        }
    }
}
