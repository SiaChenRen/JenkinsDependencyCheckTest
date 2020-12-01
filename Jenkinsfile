pipeline {
	agent any

	stages {
		
		stage('OWASP DependencyCheck') {
			steps {
				dependencyCheck additionalArguments: '--format HTML --format XML', odcInstallation: 'Default'
			}

			post {
				success {
					dependencyCheckPublisher pattern: 'dependency-check-report.xml'
				}
			}
		}

		stage('run Test'){
			agent { dockerfile { filename 'Dockerfile' reuseNode true} }
			steps {
				sh "echo 'Test Success'"
			}
		}
	}

}