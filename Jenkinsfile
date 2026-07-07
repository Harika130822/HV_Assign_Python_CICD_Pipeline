pipeline {
    agent any

    parameters {
        string(name: 'BRANCH', defaultValue: 'main', description: 'Branch to build')
        choice(name: 'ENVIRONMENT', choices: ['main','feature'], description: 'Deploy target')
    }

    environment {
        MONGO_URI = credentials('MONGO_URI_CICD')
		SECRET_KEY = credentials('SECRET_KEY_CICD')
    }

    stages {

        stage('Checkout') {
            
            steps {
                echo 'Checking out source code...'
				cleanWs()
                checkout scm 
            }
        }

        stage('Build') {
            
            steps {
                echo 'Installing dependencies...'
                
                sh '''
                    sudo apt install python3-venv -y
                    
                    python3 -m venv venv

                    . venv/bin/activate

                    python -m pip install --upgrade pip

                    python -m pip install -r requirements.txt
                '''
            }
        }
        stage('Test') {
            
            steps {
                echo 'Running unit tests...'

                sh '''
                    . venv/bin/activate

                    export PYTHONPATH=$WORKSPACE

                    python -m pytest -v
                '''
            }
        } 

        stage('Deploy') {
            
            steps {
                sh '''
                    
                    cd /home/ubuntu/apps/flask-cicd-demo

                    git fetch origin
                    git reset --hard origin/main

                    . venv/bin/activate
                    python -m pip install -r requirements.txt

                    sudo systemctl restart flask-demo

                    sleep 5

                    curl http://localhost:8000/health
                '''
            }
        }
    }

	post {
	    success {
			echo "Build completed successfully."
	        emailext(
	            subject: "SUCCESS: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
	            body: """
					Hello,
					
					Your Jenkins build completed successfully.
					
					Job Name     : ${env.JOB_NAME}
					Build Number : ${env.BUILD_NUMBER}
					Build Status : SUCCESS
					
					Build URL:
					${env.BUILD_URL}
					
					Regards,
					Jenkins CI/CD
					""",
	            to: "harikamadabathula@gmail.com"
	        )
	    }
	
	    failure {
			echo "Build failed."
	        emailext(
	            subject: "FAILED: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
	            body: """
					Hello,
					
					Your Jenkins build has failed.
					
					Job Name     : ${env.JOB_NAME}
					Build Number : ${env.BUILD_NUMBER}
					Build Status : FAILED
					
					Build URL:
					${env.BUILD_URL}
					
					Please check the console output for details.
					
					Regards,
					Jenkins CI/CD
					""",
	            to: "harikamadabathula@gmail.com"
	        )
	    }
	}
}