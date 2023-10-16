FROM eclipse-temurin:21-jdk-jammy AS builder

WORKDIR /opt/app

COPY .mvn/ .mvn
COPY mvnw pom.xml ./
RUN ./mvnw dependency:go-offline

COPY ./src ./src
RUN ./mvnw clean package

FROM eclipse-temurin:21-jre-jammy

WORKDIR /opt/app

COPY --from=builder /opt/app/target/*.jar /opt/app/*.jar

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "/opt/app/*.jar" ]
