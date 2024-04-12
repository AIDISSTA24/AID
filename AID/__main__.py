import argparse
import json
import time

import formats
from pycggen import CallGraphGenerator
from utils.constants import CALL_GRAPH_OP, KEY_ERR_OP


def main():
    #命令行参数解析工具
    parser = argparse.ArgumentParser()
    #添加一个位置参数，用于指定要处理的入口点
    parser.add_argument("entry_point", nargs="*", help="Entry points to be processed")
    #添加一个可选参数--package，用于指定包含要分析的代码的包
    parser.add_argument(
        "--package", help="Package containing the code to be analyzed", default=None
    )
    #添加一个可选参数--fasten，用于指定是否要以FASTEN格式生成调用图
    parser.add_argument(
        "--fasten",
        help="Produce call graph using the FASTEN format",
        action="store_true",
        default=False,
    )
    parser.add_argument("--product", help="Package name", default="")
    parser.add_argument(
        "--forge", help="Source the product was downloaded from", default=""
    )
    parser.add_argument("--version", help="Version of the product", default="")
    parser.add_argument(
        "--timestamp", help="Timestamp of the package's version", default=0
    )
    #添加一个可选参数--max-iter，用于指定源代码的最大迭代次数
    parser.add_argument(
        "--max-iter",
        type=int,
        help=(
            "Maximum number of iterations through source code. "
            "If not specified a fix-point iteration will be performed."
        ),
        default=-1,
    )
    #添加一个可选参数--operation，用于指定要执行的操作，可以是生成调用图或检测字典中的键错误。默认操作是生成调用图
    parser.add_argument(
        "--operation",
        type=str,
        choices=[CALL_GRAPH_OP, KEY_ERR_OP],
        help=(
            "Operation to perform. Choose "
            + CALL_GRAPH_OP
            + " for call graph generation (default) or "
            + KEY_ERR_OP
            + " for key error detection on dictionaries."
        ),
        default=CALL_GRAPH_OP,
    )

    parser.add_argument(
        "--as-graph-output", help="Output for the assignment graph", default=None
    )
    parser.add_argument("-o", "--output", help="Output path", default=None)
    #解析命令行参数并将结果存储在args变量中
    args = parser.parse_args()
    #创建一个CallGraphGenerator对象，传入命令行参数中的入口点、包、最大迭代次数和操作参数
    cg = CallGraphGenerator(
        args.entry_point, args.package, args.max_iter, args.operation
    )
    #调用CallGraphGenerator对象的analyze方法，执行分析操作
    cg.analyze()
    #CALL_GRAPH_OP == "call-graph"，检查操作参数是否为生成调用图
    if args.operation == CALL_GRAPH_OP:
        if args.fasten:
            formatter = formats.Fasten(
                cg, args.package, args.product, args.forge, args.version, args.timestamp
            )
        else:
            formatter = formats.Simple(cg)
        output = formatter.generate()
    else:
        output = cg.output_key_errs()

    as_formatter = formats.AsGraph(cg)

    if args.output:
        with open(args.output, "w+") as f:
            f.write(json.dumps(output))
    else:
        print(json.dumps(output))

    if args.as_graph_output:
        with open(args.as_graph_output, "w+") as f:
            f.write(json.dumps(as_formatter.generate()))


if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()

    # 计算程序运行时间
    execution_time = end_time - start_time
    print("程序运行时间为：", execution_time, "秒")
