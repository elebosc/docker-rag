# How to generate ollama-gguf image

Download the file `mistral-7b-v0.1.Q4_K_M.gguf` from [this repository](https://huggingface.co/TheBloke/Mistral-7B-v0.1-GGUF/blob/main/mistral-7b-v0.1.Q4_K_M.gguf) and place it in the subdirectory `models` (that also contains the `Modelfile` to be used to generate the GGUF model).

Pull `ollama/ollama` Docker image from Docker Hub:
```sh
docker pull ollama/ollama
```

Run a container using the downloaded image, in background (`-d` option) and naming it `ollama-gguf` (`--name` option):
```sh
docker run -d --name ollama-gguf ollama/ollama
```

Copy the directory `models` into the running container:
```sh
docker cp ./models/ ollama-gguf:/models/
```

To generate the GGUF model, it is necessary to operate inside the container. To do so, execute an interactive Bash shell inside it:
```sh
docker exec -it ollama-gguf /bin/bash
```

Step into `models` directory and generate the GGUF model. Name the generated model `mistralgguf`.
```sh
cd models/
ollama create -f ./Modelfile mistralgguf
```

Once the generation of the model has terminated, check that the model `mistralgguf` is effectively present among the available ones inside the container, by running the command `ollama list`.

After exiting the interactive shell inside the container with the escape sequence `Ctrl+P` `Ctrl+Q`, stop the container execution and then commit its current state into a new image, named `ollama-gguf:1.0`:
```sh
docker stop ollama-gguf
docker commit ollama-gguf ollama-gguf:1.0
```

Lastly, run a build based on the file `Dockerfile.ollama` by running the script `build-ollama-image.sh`: 
```sh
./build-ollama-image.sh
```
This build uses `ollama-gguf:1.0` as base image, copies the script `ollama_init.sh` into it and enables its execution, so that it can be used to correctly initialize the container at its startup. The new image is named `ollama-gguf:1.1`.
