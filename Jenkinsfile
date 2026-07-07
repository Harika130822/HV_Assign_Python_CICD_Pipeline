pipeline {
    agent any

    parameters {
        string(name: 'BRANCH', defaultValue: 'main', description: 'Branch to build')
        choice(name: 'ENVIRONMENT', choices: ['main','feature'], description: 'Deploy target')
    }

    environment {
        MONGO_URI = credentials('MONGO_URI_CICD')
		SECRET_KEY = credentials('SECRET_KEY_CICD')
        PORT = '5000'
    }

    stages {
        

        stage('Checkout') {
            
            steps {
                echo 'Checking out source code...'
				cleanWs()
                checkout scm 
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    sudo apt-get update
                    sudo apt-get install -y python3 python3-pip
                    sudo apt install -y python3.14-venv
                    cd ~/HV_Assign_Python_CICD_Pipeline
                    python3 -m venv venv
                    source venv/bin/activate
                    pip install flask flask-pymongo pytest
                    pip install -r requirements.txt
                    python -c "import flask; print(flask.__version__)"
                    pytest test_app.py -v --tb=short




                    python3 -m pip install --upgrade pip --break-system-packages --quiet
                    python3 -m pip install -r requirements.txt --break-system-packages --quiet
                    python3 -m pip install pytest --break-system-packages --quiet
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    python3 -m pytest test_app.py -v --tb=short
                '''
            }
        }

        stage('Deploy to Staging') {
            steps {
                sh '''
                    echo "Deploying to staging environment..."
                    pkill -f "python3 app.py" || true
                    sleep 5
                    nohup python3 app.py > app.log 2>&1 &
                    sleep 15
                    if curl -s --max-time 10 http://127.0.0.1:${PORT} > /dev/null; then
                        echo "Application is running on port ${PORT}"
                    else
                        echo "Warning: App may still be starting. Check app.log for details."
                        cat app.log || true
                        exit 1
                    fi
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