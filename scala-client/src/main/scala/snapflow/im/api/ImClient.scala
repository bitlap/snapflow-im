package snapflow.im.api

import cats.effect.{Async, Ref}
import cats.syntax.all.*
import cats.effect.std.Semaphore
import io.circe.Json
import snapflow.im.domain.{AccountScope, LocalCache}
import snapflow.im.ports.{RemoteApi, ClientCache, SocketConnector, WireCodec}

/** 根据注入的 API、缓存、连接和编解码器创建账号同步客户端。 */
object ImClient {

  /** 装配一个账号的客户端及缓存状态；网络连接由后续初始化或同步显式启动。 */
  def create[F[_]: Async](
      api: RemoteApi[F],
      scope: AccountScope,
      deviceId: String,
      cachePersistence: ClientCache[F],
      socket: SocketConnector[F],
      codec: WireCodec = snapflow.im.infrastructure.codec.JsonWireCodec
  ): F[snapflow.im.service.ImClient[F]] = for {
    cache <- Ref.of[F, Json](LocalCache.empty); gate <- Semaphore[F](1); closed <- Ref.of[F, Boolean](false)
  } yield new snapflow.im.service.ImClient(
    api.scoped(scope),
    scope,
    deviceId,
    cachePersistence,
    socket,
    cache,
    gate,
    closed,
    codec
  )
}
