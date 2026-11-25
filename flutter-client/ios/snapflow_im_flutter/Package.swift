// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "snapflow_im_flutter",
    platforms: [.iOS("13.0")],
    products: [.library(name: "snapflow-im-flutter", targets: ["snapflow_im_flutter"])],
    dependencies: [.package(name: "FlutterFramework", path: "../FlutterFramework")],
    targets: [.target(name: "snapflow_im_flutter", dependencies: [.product(name: "FlutterFramework", package: "FlutterFramework")])]
)
