package snapflow.im

/** 0.1.x 源码兼容导出。 */
type AccountScope = snapflow.im.domain.AccountScope
lazy val AccountScope = snapflow.im.domain.AccountScope
type ApiClient[F[_]] = snapflow.im.api.ApiClient[F]
lazy val ApiClient = snapflow.im.api.ApiClient
type AtomicFileCache[F[_]] = snapflow.im.infrastructure.cache.AtomicFileCache[F]
type SqliteCache[F[_]]     = snapflow.im.infrastructure.cache.SqliteCache[F]
type PostgresCache[F[_]]   = snapflow.im.infrastructure.cache.PostgresCache[F]
type ImClient[F[_]]        = snapflow.im.service.ImClient[F]
lazy val ImClient = snapflow.im.api.ImClient
type ImError = snapflow.im.domain.ImError
lazy val ImError = snapflow.im.domain.ImError
type PostgresOutbox[F[_]] = snapflow.im.infrastructure.store.PostgresOutbox[F]
lazy val JsonWireCodec = snapflow.im.infrastructure.codec.JsonWireCodec
lazy val LocalCache    = snapflow.im.domain.LocalCache
type ClientCache[F[_]] = snapflow.im.ports.ClientCache[F]
type Message           = snapflow.im.domain.Message
lazy val Message = snapflow.im.domain.Message
type NotificationIntent = snapflow.im.domain.NotificationIntent
lazy val NotificationIntent = snapflow.im.domain.NotificationIntent
type NotificationSender[F[_]] = snapflow.im.service.NotificationSender[F]
lazy val ProtocolConfig = snapflow.im.config.ProtocolConfig
type RemoteApi[F[_]] = snapflow.im.ports.RemoteApi[F]
type RetryPolicy     = snapflow.im.config.RetryPolicy
lazy val RetryPolicy = snapflow.im.config.RetryPolicy
type SocketConnector[F[_]] = snapflow.im.ports.SocketConnector[F]
type SocketSession[F[_]]   = snapflow.im.ports.SocketSession[F]
type WireCodec             = snapflow.im.ports.WireCodec

type NotificationPublisher[F[_]] = snapflow.im.ports.NotificationPublisher[F]

/** 旧版缓存名称的源码别名；新接入使用 ClientCache 与对应 Cache 实现。 */
type LocalStore[F[_]]      = ClientCache[F]
type SqliteStore[F[_]]     = SqliteCache[F]
type PostgresStore[F[_]]   = PostgresCache[F]
type AtomicFileStore[F[_]] = AtomicFileCache[F]
type JdbcOutbox[F[_]]      = PostgresOutbox[F]

/** 业务 Outbox 的领域记录、持久化端口与派发服务入口。 */
type Outbox[F[_]]                           = snapflow.im.ports.Outbox[F]
type TransactionalOutbox[F[_], Transaction] = snapflow.im.ports.TransactionalOutbox[F, Transaction]
type OutboxDispatcher[F[_]]                 = snapflow.im.service.OutboxDispatcher[F]
type OutboxClaim                            = snapflow.im.domain.OutboxClaim
lazy val OutboxClaim = snapflow.im.domain.OutboxClaim
type OutboxCompletion = snapflow.im.domain.OutboxCompletion
lazy val OutboxCompletion = snapflow.im.domain.OutboxCompletion
type OutboxState = snapflow.im.domain.OutboxState
lazy val OutboxState = snapflow.im.domain.OutboxState
