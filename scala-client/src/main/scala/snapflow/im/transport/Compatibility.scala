package snapflow.im.transport

/** 0.1.x 源码兼容导出。 */
type AuthenticatedTransport[F[_]] = snapflow.im.service.AuthenticatedTransport[F]
type HttpRequest                  = snapflow.im.ports.HttpRequest
lazy val HttpRequest = snapflow.im.ports.HttpRequest
type HttpResponse = snapflow.im.ports.HttpResponse
lazy val HttpResponse = snapflow.im.ports.HttpResponse
type HttpTransport[F[_]]      = snapflow.im.ports.HttpTransport[F]
type JdkSocketConnector[F[_]] = snapflow.im.infrastructure.jdk.JdkSocketConnector[F]
type JdkTransport[F[_]]       = snapflow.im.infrastructure.jdk.JdkTransport[F]
lazy val JdkTransport = snapflow.im.infrastructure.jdk.JdkTransport
type TokenProvider[F[_]] = snapflow.im.ports.TokenProvider[F]
