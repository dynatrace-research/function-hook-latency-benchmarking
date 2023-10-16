package sut;

import jakarta.servlet.http.HttpServletRequest;
import java.util.logging.Level;
import java.util.logging.Logger;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@SpringBootApplication
@RestController
public class HelloWorld {

  private static Logger logger = Logger.getLogger("hello-world");

  public static void main(String[] args) {
    SpringApplication.run(HelloWorld.class, args);
  }

  @RequestMapping("/")
  public String home(HttpServletRequest request) {
    if (logger.isLoggable(Level.INFO)) {
      logger.log(Level.INFO, String.format("/ was called by %s", request.getRemoteAddr()));
    }

    return "Hello World";
  }
}
