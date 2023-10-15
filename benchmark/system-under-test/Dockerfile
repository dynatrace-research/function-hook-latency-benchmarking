# ------------ build ------------
FROM eclipse-temurin:17-jdk-jammy as builder
WORKDIR /opt/app

COPY .mvn/ .mvn
COPY mvnw pom.xml ./
RUN ./mvnw dependency:go-offline

COPY ./src ./src
RUN ./mvnw clean install


# ------------ run ------------
FROM eclipse-temurin:17-jre-jammy
WORKDIR /opt/app

COPY readhook.so /opt/readhook.so

EXPOSE 8080
COPY --from=builder /opt/app/target/*.jar /opt/app/*.jar
ENTRYPOINT ["java", "-jar", "/opt/app/*.jar" ]
