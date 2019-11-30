# Data Engineering Test

Esse projeto foi desenvolvido para a realização de um teste de habilidades na matéria de Engenharia de dados.

## Getting Started

O objetivo desse projeto é solucionar através de uma arquitetura (infra-as-a-code) escalável na núvem AWS o consumo de grandes quantidades de dados, tanto em seu formato batch quanto em streaming.

Alguns desafios do projeto se encontram em:

Data cleaning em arquivos auxiliares.
Data enrichment em dados de lote e dados streaming.
Data manipulation para adicionar novos dados que serão utilizados em análises posteriores.
Data visualization em real-time e report-oriented

Arquitetura focada em AWS:

![Cloud Architecture](architecture.jpg "Cloud Architecture")

Para simular essa arquitetura localmente iremos utilizar principalmente o docker.

#### Batch use case (ETL)
- Os arquivos para o consumo se encontram na pasta /inbox
- Ao iniciar o projeto iremos simular um spark job submit para o cluster de spark que dará inicio ao processo.
- Após passar pelo processo de ETL ele será enviado para a pasta /data/inbox que é monitorada pelo Nifi.
- Ao receber um arquivo o Nifi inicia o processo de archive para o datalake do arquivo tratado (/data/datalake)
- Paralelamente o Nifi envia o lote para ser indexado no elasticsearch no indíce data tipo doc.
- Após finalização do processo pode se utilizar tanto o Jupyter consultando diretamente os arquivos no datalake quanto o Kibana para explorar os dados no datalake.
#### Stream use case
- É enviado um post para a API.
- O nifi recepciona o evento em formato de flowfile
- O nifi enriquece os dados do evento com os dados auxiliares disponibilizado
- O nifi indexa o evento tornando-o disponível para explorações no dashboard realtime do kibana

### Extra use case (ELT)
Existe um outro caso onde a informação precisa ser consumida e e já estar disponível para exploração no menor tempo de disponibilidade possível. Seria essa utilizando a metodologia ELT. Porém com o risco de fazer a transformação via alguma ferramenta de exploração.
- Recepção dos arquivos pelo S3
- Consumo dos arquivos pelo Nifi
- Conversão dos arquivos de JSON para Parquet da forma com que eles chegam
- Disponibilização dos dados no S3 na zona processada
- Transformação dos dados utilizando Athena
- Extração da informação

### Prerequisites

Para a replicação bem sucedida desse projeto é necessário possuir alguns requisitos instalados em seus sistema operacional linux.

Para esse tutorial estarei utilizando um distribuição do Debian. Linux Mint
Caso o sistema operacional seja outro por favor siga esse tutorial: 

https://runnable.com/docker/install-docker-on-linux

Instalando o docker
```
sudo apt-get update -y && sudo apt-get install -y linux-image-extra-$(uname -r)
```
```
sudo apt-get install docker-engine -y
```
```
sudo service docker start
```

## Deployment

Após ter o docker instalado é necessário baixar as imagens dos serviços existentes no servidor, são eles:

Standalone Spark Cluster
Standalone Nifi Cluster
Standalone Elasticsearch Cluster + Standalone Kibana Cluster

Para automatizar o trabalho utilizar o arquivo docker-compose.yml na raiz do projeto, ele já faz o pull das imagens e configura a persistência e os objetos de rede necessários.

Para maiores informações sobre o docker-compose verificar o conteúdo documentado do arquivo.

Mover para a pasta onde está o arquivo docker-compose.yml 
```
cd /path/para/servidor/
```

Executar o servidor vinculado ao terminal
```
docker-compose up
```

Executar o servidor em background
```
docker-compose up -d
```

É importante ressaltar aqui que alguns serviços podem demorar alguns minutos para inicializar.
Por isso montei um shell script para verificar se os sistemas estiverem online.
```
./healthcheck.sh
```

## Services

Após o serviço ter inicializado completamente você poderá navegar pelas UI's dos serviços utilizados

Nifi UI - http://localhost:8080/nifi
Kibana UI - http://localhost:5601
Elasticsearch Server - http://localhost:4571/_cat/health

## Running

Passo a passo para rodar as aplicações

### Batch Use Case

* Importar os arquivos que devem ser processado para a pasta /inbox na raiz do projeto.
* Iremos executar o comando que irá simular um spark job submit para executar um script pyspark no cluster de spark.
```
docker exec -it taxi_spark_1 python3 /home/jovyan/work/scripts/data_preparation.py
```
* Após o término do processamento você poderá acompanhar o recebimento do arquivo e seu roteamento na UI do Nifi. http://localhost:8080/nifi
* Após ser consumido e arquivado pelo Nifi ele irá splitar os registros em blocos de 5.000 para não sobrecarregar o Elasticsearch e iniciará o processo de indexação. Nome do processor:  "Batch - Index on Elasticsearch"
* Após ou durante a conclusão de todos as splits parts, o usuário já poderá visualizar o Dashboard Geral com as informações do dataset: http://localhost:5601/app/kibana#/dashboard/713493f0-1192-11ea-8ba2-f74df6efb357

PS: Importante ressaltar que o processo de ingestão pode demorar alguns minutos pois depende da memória da JVM a qual eu deixei configurada para usar no máximo 512 MB. Caso haja interesse de fazer um fine-tunning, vou descrever em outra sessão como fazer a alteração.

### Stream Use Case
* A inicialização do servidor já disponibiliza uma API REST aberta apenas para o metódo Post na porta 8989 no endpoint http://localhost:8989/taxiStream.
* Para acompanhar em real-time acesse a url do dashboard em tempo real: http://localhost:5601/app/kibana#/dashboard/72884a60-1211-11ea-adf4-af3007798d61
PS: Esse dashboard está filtrando apenas o mês vigente, por esse motivo o POST abaixo deve ter o pickup_datetime referente ao mês atual. Ou deve ser atualizado no date picker do kibana. =) 
* O usuário deverá fazer um post nesse endpoint.
```
curl -d '{"vendor_id":"CMT","pickup_datetime":"2019-11-21T18:51:11.767205+00:00","dropoff_datetime":"2019-11-21T18:57:09.433767+00:00","passenger_count":2,"trip_distance":0.8,"pickup_longitude":-74.004114,"pickup_latitude":40.74295,"rate_code":null,"store_and_fwd_flag":null,"dropoff_longitude":-73.994712,"dropoff_latitude":40.74795,"payment_type":"Cash","fare_amount":5.4,"surcharge":0,"tip_amount":0,"tolls_amount":0,"total_amount":5.4}' -H "Content-Type: application/json" -X POST http://localhost:8989/taxiStream
```
* Acompanhar no dashboard a atualização de dados que está com o default de refresh de 10 segundos.


### Extra Use Case


## Analysis

Os resultados das análises estão no arquivo analysis.html na raiz do projeto. 
Os códigos de spark utilizados para manipular o dataset estão em scripts/data_preparation
Os gráficos e o mapa foram gerados utilizando o Kibana
O HTML analysis foi criado utilizando o draw.io

## Built With

* [Docker](https://www.docker.com/) - Deploy containerized application
* [Apache Nifi](https://nifi.apache.org/) - Data Streaming solution
* [Apache Spark](https://spark.apache.org/) - Distributed programing for bigdata solution
* [Elasticsearch](https://www.elastic.co/pt/) - Index persistance of data
* [Kibana](https://www.elastic.co/pt/products/kibana) - Data visualization tool

## Authors

* **André Petridis** - [Linkedin](https://www.linkedin.com/in/andrepetridis/)