"""Boto3 Mock Module"""
import unittest
from typing import Any

response = ["https://bevor-media.s3.amazonaws.com/123-456/fa7d08b1-b448-4ea4-a514-b929011387b1/fa7d08b1-b448-4ea4-a514-b929011387b1-image.jpeg?AWSAccessKeyId=ASIAS4YHYXTXVKYECWHA&Signature=462Txu5C4IF5HIiTa8qyltBI0VI%3D&x-amz-security-token=IQoJb3JpZ2luX2VjEEYaCXVzLXdlc3QtMSJHMEUCIE6WvvX3yGU%2B7Mb0s8evr4AXxdHipMSBerjq4D8Rvbm8AiEAxmV1vJvO3F8FNltLnzLtGVDjE8pstq3wXMHt4%2BpENLUqggMIHxACGgwxOTkxOTU0MDk2NDciDP7L8RO8%2BIplXAD%2B8CrfAlqRKz4A%2FOlV%2FbJVI0u9Uu4qlmU5ibRWPb6RlbnxMPuIZPMMyffjrh6fl1okMiw4E5rhYDVpVMJjVMvN9SmTG4acxwcYytahF4ZlDLSTSqpoXuj7YR8tJwYyGG5UMWkinGMPOQ7ReqeQCkLIVWnLZuXoQo0sEYo2F9MFe5A7gY2AxiTrz%2FQN6RcLQ1Qc7J%2BBAH789oE0ll2tHsUI9mWKq6lFRP8fnEkp%2B6zIQVPqG27Ot7x%2B1YHqvyzkTHpyAffWCQn9jL0qVz%2FYMkD0mPCiS1j6zPq2DIDJyNyLAHdTeKtbrycTWxdHyMi3ZfSv2%2FIXzeC9Sxe0l09Xb1joPXOV9MiZ2VhRuN5lkLKGeH%2BamDbAKHsrGKTKeVnopeL9MnEkMSTsAmlq0Wx%2F60CrVCR9mhnkwX0ICssaP9SoHkbCA7fkIGjg51xo4vLoPEczg0aDcFmNXOSrV6J4Go6Z80y4YTDJmea0BjqeAUfzrKICn4U84Ijxwr8Ah8IRndozQkLoKO%2Bc08MrICFTjhykqPJ1oPKJe3ioeidigsrnXyM8AvHHkMZzuOl4R75p1keLySvl25B9cTm1wJwutpEoEktniZSsICaJ5EJjHmXQEvcXTNOK2zrlryoDzrZCT77ayHcYfdAy2ogq82NhkybccGl6CA5tVMrhsqnbu7UPsohFqvJb1Nok9xeQ&Expires=1721342682",
            "https://bevor-media.s3.amazonaws.com/123-456/fa7d08b1-b448-4ea4-a514-b929011387b1/fa7d08b1-b448-4ea4-a514-b929011387b1-thumb.jpeg?AWSAccessKeyId=ASIAS4YHYXTXVKYECWHA&Signature=psrwfJuQZdDKJ9hOQdw6Ca8mB0w%3D&x-amz-security-token=IQoJb3JpZ2luX2VjEEYaCXVzLXdlc3QtMSJHMEUCIE6WvvX3yGU%2B7Mb0s8evr4AXxdHipMSBerjq4D8Rvbm8AiEAxmV1vJvO3F8FNltLnzLtGVDjE8pstq3wXMHt4%2BpENLUqggMIHxACGgwxOTkxOTU0MDk2NDciDP7L8RO8%2BIplXAD%2B8CrfAlqRKz4A%2FOlV%2FbJVI0u9Uu4qlmU5ibRWPb6RlbnxMPuIZPMMyffjrh6fl1okMiw4E5rhYDVpVMJjVMvN9SmTG4acxwcYytahF4ZlDLSTSqpoXuj7YR8tJwYyGG5UMWkinGMPOQ7ReqeQCkLIVWnLZuXoQo0sEYo2F9MFe5A7gY2AxiTrz%2FQN6RcLQ1Qc7J%2BBAH789oE0ll2tHsUI9mWKq6lFRP8fnEkp%2B6zIQVPqG27Ot7x%2B1YHqvyzkTHpyAffWCQn9jL0qVz%2FYMkD0mPCiS1j6zPq2DIDJyNyLAHdTeKtbrycTWxdHyMi3ZfSv2%2FIXzeC9Sxe0l09Xb1joPXOV9MiZ2VhRuN5lkLKGeH%2BamDbAKHsrGKTKeVnopeL9MnEkMSTsAmlq0Wx%2F60CrVCR9mhnkwX0ICssaP9SoHkbCA7fkIGjg51xo4vLoPEczg0aDcFmNXOSrV6J4Go6Z80y4YTDJmea0BjqeAUfzrKICn4U84Ijxwr8Ah8IRndozQkLoKO%2Bc08MrICFTjhykqPJ1oPKJe3ioeidigsrnXyM8AvHHkMZzuOl4R75p1keLySvl25B9cTm1wJwutpEoEktniZSsICaJ5EJjHmXQEvcXTNOK2zrlryoDzrZCT77ayHcYfdAy2ogq82NhkybccGl6CA5tVMrhsqnbu7UPsohFqvJb1Nok9xeQ&Expires=1721342682"]


class BogoClient:
    """Mock"""
    presigned_mock = unittest.mock.Mock(side_effect=response)

    def __init__(self, *_args: Any, **_kwargs: Any) -> None:
        """Mock bogo3.client(arg)"""
        pass

    def generate_presigned_url(self, *_args: Any, **_kwargs: Any) -> Any:
        """Mock Boto3 Presigned Url"""
        return self.presigned_mock()

    def put_object(self, *_args: Any, **_kwargs: Any) -> None:
        """Mock Boto3 Put Object"""
        pass
