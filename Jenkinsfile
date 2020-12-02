pipeline {
	agent any

	environment {
		SCANNER_HOME =  tool 'DefaultTest'
    }

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



		stage('Run Tests') {
			parallel {


				stage('SonarQube analysis') {
					steps {
						withSonarQubeEnv('Default') {
							sh "$SCANNER_HOME/bin/sonar-scanner"
						}
					}
				}

				stage('Selenium Test') {
					agent { dockerfile { filename 'Dockerfile' reuseNode true} }

					steps {
					sh "py.test --junitxml tests/selenium_test_result.xml tests/selenium_test.py"
					}

					post {
						always {
							junit 'tests/*.xml'
						}					
					}
				}

			}
		}
	}
}
