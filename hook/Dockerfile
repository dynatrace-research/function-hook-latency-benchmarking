FROM gcc:7.5.0 AS builder

WORKDIR /

COPY Makefile ./
COPY ./src ./src

RUN mkdir -p ./out
RUN make

FROM alpine:3.18.4

WORKDIR /

COPY --from=builder /out/ /out/

CMD ["/bin/sleep", "infinite"]
