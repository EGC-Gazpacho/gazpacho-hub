
        function show_upload_dataset() {
            document.getElementById("upload_dataset").style.display = "block";
        }

        function generateIncrementalId() {
            return currentId++;
        }
    
        function check_info() {
            let commitMessage = document.querySelector('input[name="commit_message"]');
            let owner = document.querySelector('input[name="owner"]');
            let repo_name = document.querySelector('input[name="repo_name"]');
            let token = document.querySelector('input[name="access_token"]');

            commitMessage.classList.remove("error");
            owner.classList.remove("error");
            repo_name.classList.remove("error");
            token.classList.remove("error");
            clean_upload_errors();


            let commitMessageLength = commitMessage.value.trim().length;
            let ownerLength = owner.value.trim().length;
            let repo_nameLength = repo_name.value.trim().length;
            let tokenLength = token.value.trim().length;

           if (commitMessageLength < 3) {
               write_upload_error("Commit message must be of minimum length 3");
               commitMessage.classList.add("error");
           }
           if (ownerLength < 1) {
               write_upload_error("Repository owner is required");
               owner.classList.add("error");
           }
              if (repo_nameLength < 1) {
                write_upload_error("Repository name is required");
                repo_name.classList.add("error");
              }

                if (tokenLength < 1) {
                    write_upload_error("Access token is required");
                    token.classList.add("error");
                }
           return (commitMessageLength >= 3 && ownerLength > 0  && repo_nameLength > 0 && tokenLength > 0);
        }

 

        function show_loading() {
            document.getElementById("upload_button_github").style.display = "none";
            document.getElementById("loading").style.display = "block";
        }

        function hide_loading() {
            document.getElementById("upload_button_github").style.display = "block";
            document.getElementById("loading").style.display = "none";
        }

    
        function clean_upload_errors() {
            let upload_error = document.getElementById("upload_error");
            upload_error.innerHTML = "";
            upload_error.style.display = 'none';
        }

        function write_upload_error(error_message) {
            let upload_error = document.getElementById("upload_error");
            let alert = document.createElement('p');
            alert.style.margin = '0';
            alert.style.padding = '0';
            alert.textContent = 'Upload error: ' + error_message;
            upload_error.appendChild(alert);
            upload_error.style.display = 'block';
        }



        window.onload = function () {

            document.getElementById('upload_button_github').addEventListener('click', function () {
        
                clean_upload_errors();
                show_loading();
        
                let check = check_info();  
                if (check) {
        
                    if (dropzoneInstanceGithub && dropzoneInstanceGithub.getAcceptedFiles().length > 0) {
                        const formData = new FormData();
                        formData.append("commit_message", document.getElementById('commit_message').value);  
                        formData.append("owner", document.getElementById('owner').value);
                        formData.append("repo_name", document.getElementById('repo_name').value);
                        formData.append("repo_type", document.getElementById('repo_type').value);
                        formData.append("access_token", document.getElementById('access_token').value);
                        formData.append("license", document.getElementById('license').value);
        
                        dropzoneInstanceGithub.getAcceptedFiles().forEach(function(file) {
                            formData.append("file", file); 
                        });
        
                        fetch('/github/upload', {
                            method: 'POST',
                            body: formData
                        })
                        .then(response => {
                            const errorContainer = document.getElementById('upload_github_error');
                            if (!response.ok) {
                                if (response.status === 401) {
                                    errorContainer.style.display = 'block';
                                    document.getElementById('error_message').textContent = "Error to upload the file: " + response.statusText + " (ERROR-"+ response.status + "), verify your access token.";
                                    hide_loading();
                                    throw new Error("Bad credentials. Verify your access token.");
                                    
                                } else if (response.status === 404 || response.status === 400) {
                                    errorContainer.style.display = 'block';
                                    document.getElementById('error_message').textContent = "Error to upload the file: " + response.statusText + " (ERROR-"+ response.status + "), verify the repository owner and name.";
                                    hide_loading();
                                    throw new Error("Repository not found. Verify the repository owner and name.");
                                }
                                else if (response.status === 422) {
                                    errorContainer.style.display = 'block';
                                    document.getElementById('error_message').textContent = "Error to upload the file: " + response.statusText + " (ERROR-"+ response.status + "), you have in your repository a file with the same name.";
                                    hide_loading();
                                    throw new Error("Repository not found. Verify the repository owner and name.");
                                }
                                
                                else {
                                    errorContainer.style.display = 'block';
                                    document.getElementById('error_message').textContent = "Error to upload the file: " + response.statusText + " (ERROR-"+ response.status + ")";
                                    hide_loading();
                                    throw new Error(`Error ${response.status} - ${response.statusText}`);
                                }
                            }
                            return response.json();
                        }).catch(error => {
                            const errorContainer = document.getElementById('upload_github_error');
                             errorContainer.style.display = 'block';
                             document.getElementById('error_message').textContent = "Error to upload the file: " + response.statusText + " (ERROR-"+ response.status + ")";
                             console.error('Error:', error);
                            hide_loading();
                        })
                        
                        
                        
                        .then(data => {
                            if (data.message) {
                                console.log('Success:', data.message);
                            }
                            //window.location.href = "/";
                            hide_loading(); 
                            const errorContainer = document.getElementById('upload_github_error');
                            errorContainer.style.display = 'none';                        
                        });
                    } else {
                        hide_loading(); 
                    }
                } else {
                    hide_loading();  
                }
            });
        };
                   
              
                
       
        function toBase64(str) {
            return btoa(String.fromCharCode(...new TextEncoder().encode(str)));
        }
        


        function isValidOrcid(orcid) {
            let orcidRegex = /^\d{4}-\d{4}-\d{4}-\d{4}$/;
            return orcidRegex.test(orcid);
        }