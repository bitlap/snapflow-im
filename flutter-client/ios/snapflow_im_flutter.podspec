Pod::Spec.new do |s|
  s.name = 'snapflow_im_flutter'
  s.version = '0.1.1'
  s.summary = 'SnapFlow IM iOS APNs adapter'
  s.homepage = 'https://github.com/bitlap/snapflow-im'
  s.license = { :type => 'Apache-2.0' }
  s.author = { 'bitlap' => 'https://github.com/bitlap' }
  s.source = { :path => '.' }
  s.source_files = 'snapflow_im_flutter/Sources/snapflow_im_flutter/**/*.swift'
  s.dependency 'Flutter'
  s.platform = :ios, '13.0'
  s.swift_version = '5.0'
end
