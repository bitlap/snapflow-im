package snapflow.im.examples

import cats.effect.Async
import snapflow.im.api.{ApiClient, ImClient as ImClientFactory}
import snapflow.im.domain.AccountScope
import snapflow.im.ports.{HttpTransport, TokenProvider, ClientCache, SocketConnector, WireCodec}
import snapflow.im.service.{AuthenticatedTransport, ImClient}
import snapflow.im.infrastructure.codec.JsonWireCodec

object ClientWiring {
  def create[F[_]: Async](
      transport: HttpTransport[F],
      tokens: TokenProvider[F],
      scope: AccountScope,
      deviceId: String,
      store: ClientCache[F],
      socket: SocketConnector[F],
      codec: WireCodec = JsonWireCodec
  ): F[ImClient[F]] =
    ImClientFactory.create(
      new ApiClient(new AuthenticatedTransport(transport, tokens), codec = codec),
      scope,
      deviceId,
      store,
      socket,
      codec
    )
}
